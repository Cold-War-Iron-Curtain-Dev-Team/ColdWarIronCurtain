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
			Out.vTexCoord0.y = -Out.vTexCoord0.y;
		
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
			if( v.vTexCoord0.x <= CurrentState )
				return vFirstColor;
			else
				return vSecondColor;
		}
		
	]]

	MainCode PixelTexture
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float4 texColor = tex2D(TextureOne, v.vTexCoord0.xy);
			if (texColor.a == 0) return float4(0, 0, 0, 0);
			
			float alpha = vFirstColor.r;
			float paletteWidth = vFirstColor.g * 100.f;
			float correction = 0.01;
			float xCoord = CurrentState * (10000 / paletteWidth) - correction;
			float yCoord = 0;

			float frameWidth = vSecondColor.r * 1000.f;
			float frameHeight = vSecondColor.g * 1000.f;

			float BorderSize = vSecondColor.a * 1000.f;
			bool isOnEdge = tex2D(TextureOne, v.vTexCoord0.xy + float2(BorderSize/frameWidth, BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(-BorderSize/frameWidth, -BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(0/frameWidth, BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(BorderSize/frameWidth, 0/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(-BorderSize/frameWidth, 0/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(0/frameWidth, -BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(-BorderSize/frameWidth, BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(-BorderSize/frameWidth, BorderSize/frameHeight)).a == 0;



			// Construct Fill Color
			float4 fillColor = tex2D(TextureTwo, float2 (xCoord, yCoord));
			if (fillColor.a == 0) return texColor;

			if(isOnEdge) {
				fillColor.rgb *= 1.5f;
			}

			// Overlay & Return
			float3 displayColor = texColor.rgb * (1 - alpha) + fillColor.rgb * alpha;
			return float4(displayColor.r, displayColor.g, displayColor.b, 1.0);
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

