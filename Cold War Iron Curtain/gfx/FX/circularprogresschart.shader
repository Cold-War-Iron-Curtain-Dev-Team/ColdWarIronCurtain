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
	float4 vFirstColor;
	float4 vSecondColor;
	float CurrentState;
};


VertexShader =
{
	MainCode VertexShader
	[[
		
		VS_OUTPUT main(const VS_INPUT v )
		{
			VS_OUTPUT Out;
		   	Out.vPosition  = mul( WorldViewProjectionMatrix, v.vPosition );
			Out.vTexCoord0  = v.vTexCoord;

			return Out;
		}
		
	]]
}

PixelShader =
{
	MainCode PixelColor
	[[
		
		float4 main( VS_OUTPUT v ) : PDX_COLOR
{
    // 1. Circle masking
    float2 uv = v.vTexCoord0 - 0.5f;
    float distance = length(uv);
    if (distance > 0.5f) discard; // Cutoff for circle shape
    
    // 2. Progress calculation (0-1 to 0-2π)
    float progress = CurrentState * 6.283185307f; // 2π
    
    // 3. Angle calculation (clockwise from top)
    float angle = atan2(uv.y, -uv.x) - 1.5707963268f; // Offset to start from top
    if(angle < 0) angle += 6.283185307f; // Normalize to 0-2π
    
    // 4. Color selection
    if(angle < progress) {
        return vFirstColor;
    }
    
    // 5. Anti-aliased edge
    float edge = smoothstep(0.48f, 0.5f, distance);
    return lerp(vSecondColor, float4(0,0,0,0), edge);
}
		
	]]

	MainCode PixelTexture
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
            return float4(1, 1, 1, 1);
		}
		
		
	]]
}


BlendState BlendState
{
	BlendEnable = yes
	SourceBlend = "SRC_ALPHA"
	DestBlend = "INV_SRC_ALPHA"
}


Effect Color
{
	VertexShader = "VertexShader"
	PixelShader = "PixelColor"
}

Effect Texture
{
	VertexShader = "VertexShader"
	PixelShader = "PixelTexture"
}

