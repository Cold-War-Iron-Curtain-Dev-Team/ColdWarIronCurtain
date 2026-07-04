Includes = {
}

PixelShader =
{
    Samplers =
    {
        TextureOne =
        {
            Index = 0
            MagFilter = "Point"
            MinFilter = "Point"
            MipFilter = "None"
            AddressU = "Wrap"
            AddressV = "Wrap"
        }
        TextureTwo =
        {
            Index = 1
            MagFilter = "Point"
            MinFilter = "Point"
            MipFilter = "None"
            AddressU = "Wrap"
            AddressV = "Wrap"
        }
    }
}

VertexStruct VS_INPUT
{
    float4 vPosition  : POSITION;
    float2 vTexCoord  : TEXCOORD0;
};

VertexStruct VS_OUTPUT
{
    float4  vPosition : PDX_POSITION;
    float2  vTexCoord0 : TEXCOORD0;
};

ConstantBuffer( 0, 0 )
{
    float4x4 WorldViewProjectionMatrix;
    float4 vFirstColor;   // rgb = filled color,  a = TOTAL_SEATS
    float4 vSecondColor;  // rgb = unfilled col, a = ROWS (0 = auto)
    float  CurrentState;  // SEATS_SECURED (or 0..1 fraction)
};

VertexShader =
{
    MainCode VertexShader
    [[
        VS_OUTPUT main( const VS_INPUT v )
        {
            VS_OUTPUT Out;
            Out.vPosition  = mul( WorldViewProjectionMatrix, v.vPosition );
            Out.vTexCoord0 = v.vTexCoord;
            return Out;
        }
    ]]
}

PixelShader =
{
    MainCode PixelColor
    [[
        // ---- helper math ----
        float2 ToPolar(float2 p) { return float2(length(p), atan2(p.y, p.x)); }
        float2 FromPolar(float r, float t) { return float2(r * cos(t), r * sin(t)); }
        float  aastep(float edge, float x, float w) { return smoothstep(edge - w, edge + w, x); }

        float row_radius(int j, int rows, float innerR, float outerR, float curvature)
        {
            if (rows <= 1) return outerR;
            float t  = float(j) / float(rows - 1);
            float t2 = lerp(t, pow(t, 1.0 + curvature * 1.5), curvature); // bias toward outer
            return lerp(innerR, outerR, t2);
        }

        float4 main( VS_OUTPUT v ) : PDX_COLOR
        {
            // map uv 0..1 -> -1..1; flip Y so arc opens upward
            float2 uv = v.vTexCoord0 * 2.0 - 1.0;
            float2 p  = float2(uv.x, uv.y) * 0.97; // 5% shrink to keep dots inside the box

            // input params
            int totalSeats = max(1, int(round(vFirstColor.a)));
            // accept either absolute seats or a 0..1 fraction in CurrentState
            float cs = CurrentState;
            int filled = (cs <= 1.001) ? int(round(cs * float(totalSeats))) : int(round(cs));
            filled = clamp(filled, 0, totalSeats);

            int rowsParam = int(round(vSecondColor.a));
            // auto rows heuristic ~ sqrt(N); clamp to [3..8]
            int rows = (rowsParam > 0) ? rowsParam : clamp( int(round( sqrt( float(totalSeats) / 9.0 ) )), 3, 8 );

            // look constants (tweak here if you want a different shape)
			// Dynamic band: fewer total seats means tighter rows (larger innerR),
			// and slightly straighter spacing (lower curvature)
			float tight = saturate( (180.0 - float(totalSeats)) / 360.0 ); // kicks in below ~180 seats

			float innerR    = lerp(0.60, 0.70, tight);  // up to +0.10 tighter when seats are low
			float outerR    = 0.92;                     // keep same margin so sides don't clip
			float curvature = lerp(0.12, 0.08, tight);  // a bit more even spacing when tight

			const float dotR = 0.019;   // keep your working dot size
			const float aa   = 0.0035;


            // only draw inside semicircle (theta in [0..pi])
            float2 pol   = ToPolar(p);
            float theta  = pol.y;
            if (theta < 0.0 || theta > 3.14159265) return float4(0,0,0,0);

            // row weights ~ half-circumference (pi * r_j)
            float sumW = 0.0;
            for (int j = 0; j < 8; ++j)
            {
                if (j >= rows) break;
                float rj = row_radius(j, rows, innerR, outerR, curvature);
                sumW += 3.14159265 * rj;
            }
            sumW = max(sumW, 1e-6);

            // find nearest dot center across rows
            float bestD = 1e9;
            int   bestRow = -1;
            int   bestN   = 1;
            int   bestK   = 0;
            float bestR   = 1.0;

            for (int j = 0; j < 8; ++j)
            {
                if (j >= rows) break;
                float rj = row_radius(j, rows, innerR, outerR, curvature);

                // seats on this row (continuous weight to integer)
                int n = max(1, int(round( (3.14159265 * rj / sumW) * float(totalSeats) )));
				float dTh = 3.14159265 / float(max(n,1));

				// snap to sector, then place the center at the midpoint of that sector
				float kf = floor(theta / dTh);
				kf = clamp(kf, 0.0, float(n - 1));
				int   k   = int(kf);
				float thC = (kf + 0.5) * dTh;   // midpoint avoids the 0/pi seam
				float2 c  = FromPolar(rj, thC);

                float d = length(p - c);
                if (d < bestD) { bestD = d; bestRow = j; bestN = n; bestK = k; bestR = rj; }
            }

            // dot shape with AA edge
            float inside = 1.0 - aastep(dotR, bestD, aa);
            if (inside <= 0.0) return float4(0,0,0,0);

            // compute global seat index via weight prefix (no arrays)
            float wBefore = 0.0;
            for (int j = 0; j < 8; ++j)
            {
                if (j >= bestRow) break;
                float rj = row_radius(j, rows, innerR, outerR, curvature);
                wBefore += 3.14159265 * rj;
            }
			int prefixSeats = int(floor( (wBefore / sumW) * float(totalSeats) + 1e-4 ));

			// use a different name so we don't shadow float2 p above
			float prog = (CurrentState <= 1.001)
					   ? saturate(CurrentState)                           // 0..1 fraction
					   : saturate(CurrentState / float(totalSeats));      // seats to fraction

			// seats to fill on THIS row, based on fraction
			int rowFilled = int(floor(prog * float(bestN) + 1e-5));

			// k=0 is rightmost; convert to "index from LEFT"
			int kFromLeft = (bestN - 1) - bestK;

			// column-wise fill: left to right, same fraction on all rows
			bool isFilled = (kFromLeft < rowFilled);

            float4 filledCol   = float4(vFirstColor.rgb, 1.0);
            float4 unfilledCol = float4(vSecondColor.rgb, 1.0);
            float4 outCol      = isFilled ? filledCol : unfilledCol;
            outCol.a *= inside;
            return outCol;
        }
    ]]

    MainCode PixelTexture
    [[
        float4 main( VS_OUTPUT v ) : PDX_COLOR
        {
            return float4(1,1,1,1);
        }
    ]]
}

BlendState BlendState
{
    BlendEnable = yes
    SourceBlend = "SRC_ALPHA"
    DestBlend   = "INV_SRC_ALPHA"
}

Effect Color
{
    VertexShader = "VertexShader"
    PixelShader  = "PixelColor"
}

Effect Texture
{
    VertexShader = "VertexShader"
    PixelShader  = "PixelTexture"
}
