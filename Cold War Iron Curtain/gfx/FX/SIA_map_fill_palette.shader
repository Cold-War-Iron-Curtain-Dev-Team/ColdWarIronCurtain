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
		//All credits to TNO Guangdong Team	
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			
			float4 texColor = tex2D(TextureOne, v.vTexCoord0.xy);
			if (texColor.a == 0) return float4(0, 0, 0, 0);
			
			float numColors = vFirstColor.r * 1000.f;
			float inputFrame = CurrentState * 10000.f;
			float color = floor(inputFrame/1000.f) - 1;
			float opacity = saturate(mod(inputFrame, 1000.f) / 100.f);
			float alpha = vFirstColor.a;

			float frameWidth = vSecondColor.r * 1000.f;
			float frameHeight = vSecondColor.g * 1000.f;

			float PaletteSize = vSecondColor.b * 1000.f;
			float rescale = PaletteSize/frameHeight;
			if(frameWidth>frameHeight)  {
				float rescale = PaletteSize/frameWidth;
			}

			float imgX = (v.vTexCoord0.x - (1.0 - rescale)/1.9) / rescale;
			float imgY = (v.vTexCoord0.y + (1.0 - rescale)/2.3) / rescale;

			if(frameWidth>frameHeight) {
				float toCrop = (frameWidth-frameHeight) / (2*frameWidth);
				imgX = (imgX - toCrop) / (1.0 - 2 * toCrop);
			}
			else {
				float toCrop = (frameHeight-frameWidth) / (2*frameHeight);
				imgY = (imgY - toCrop) / (1.0 - 2 * toCrop);
			}


			float BorderSize = vSecondColor.a * 1000.f;
			bool isOnEdge = tex2D(TextureOne, v.vTexCoord0.xy + float2(BorderSize/frameWidth, BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(-BorderSize/frameWidth, -BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(0/frameWidth, BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(BorderSize/frameWidth, 0/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(-BorderSize/frameWidth, 0/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(0/frameWidth, -BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(-BorderSize/frameWidth, BorderSize/frameHeight)).a == 0 ||
							tex2D(TextureOne, v.vTexCoord0.xy + float2(-BorderSize/frameWidth, BorderSize/frameHeight)).a == 0;

			float4 fillColor = tex2D(TextureTwo, float2((color + 0.1f) * (1.0f / numColors), 0));
			if (imgX > 0.001f && imgX < 1 && imgY <= 0  && imgY >= -1 && !isOnEdge) {
				fillColor = tex2D(TextureTwo, float2((color + imgX) * (1.0f / numColors), imgY));
			}

			if(isOnEdge) {
				fillColor.rgb *= 1.5f;
			}
			else {
				fillColor.rgb *= (0.5f + opacity * 0.5f);
			}

			float3 displayColor = texColor.rgb * alpha + fillColor.rgb * (1 - alpha);
			return float4(displayColor.rgb, 1.0);
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

