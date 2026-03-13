import type { ClawMateConfig } from "./core/types";

export interface GenerateVideoOptions {
  config: ClawMateConfig;
  baseImageUrl: string;
  prompt: string;
  duration?: number;
  aspectRatio?: string;
  logger: any;
}

export interface VideoResult {
  ok: boolean;
  videoUrl?: string;
  previewUrl?: string;
  provider?: string;
  requestId?: string;
  message?: string;
  error?: string;
}

function extractVideoUrl(html: string): { videoUrl: string; previewUrl: string } {
  const videoMatch = html.match(/src="([^"]+\.mp4)"/);
  const previewMatch = html.match(/poster="([^"]+\.jpg)"/);
  
  return {
    videoUrl: videoMatch ? videoMatch[1] : '',
    previewUrl: previewMatch ? previewMatch[1] : ''
  };
}

export async function generateVideo(options: GenerateVideoOptions): Promise<VideoResult> {
  const { config, baseImageUrl, prompt, duration = 6, aspectRatio = "16:9", logger } = options;
  
  const videoProviderName = config.videoProvider || config.defaultProvider;
  const provider = config.providers[videoProviderName];
  
  if (!provider) {
    return {
      ok: false,
      error: `Video provider ${videoProviderName} not found`,
      message: "视频生成配置错误"
    };
  }

  // 检查是否为HTTP URL
  if (!baseImageUrl.startsWith("http://") && !baseImageUrl.startsWith("https://")) {
    logger.error("视频生成需要HTTP URL格式的图片", { 
      baseImageUrl,
      hint: "请确保传入的是originalImageUrl而不是本地路径"
    });
    return {
      ok: false,
      error: "图片URL格式错误",
      message: "视频生成需要HTTP URL格式的参考图片"
    };
  }

  try {
    const model = provider.model;
    if (!model) {
      return {
        ok: false,
        provider: videoProviderName,
        requestId: null,
        message: "视频生成失败",
        error: `Provider "${videoProviderName}" missing model configuration`
      };
    }

    const requestBody = {
      model,
      messages: [
        {
          role: "user",
          content: [
            {
              type: "image_url",
              image_url: {
                url: baseImageUrl
              }
            },
            {
              type: "text",
              text: prompt
            }
          ]
        }
      ],
      video_config: {
        aspect_ratio: aspectRatio,
        video_length: duration,
        resolution_name: "480p",
        preset: "normal"
      },
      stream: true  // 使用流式响应
    };

    logger.info("调用视频生成接口", {
      provider: videoProviderName,
      imageUrl: baseImageUrl,
      prompt,
      duration,
      aspectRatio
    });

    const response = await fetch(`${provider.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${provider.apiKey}`
      },
      body: JSON.stringify(requestBody),
      signal: AbortSignal.timeout(provider.timeoutMs || 300000)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const text = await response.text();
    
    // 从流式响应中提取视频内容
    const lines = text.split('\n').filter(line => line.startsWith('data: '));
    let videoContent = '';
    
    for (const line of lines) {
      if (line === 'data: [DONE]') break;
      
      try {
        const data = JSON.parse(line.substring(6));
        const content = data.choices?.[0]?.delta?.content;
        if (content) {
          videoContent += content;
        }
      } catch (e) {
        // 忽略解析错误
      }
    }

    if (!videoContent) {
      throw new Error("未能从响应中提取视频内容");
    }

    // 提取video标签中的URL
    const { videoUrl, previewUrl } = extractVideoUrl(videoContent);

    if (!videoUrl) {
      throw new Error("未能解析视频URL");
    }

    logger.info("视频生成成功", {
      provider: videoProviderName,
      videoUrl,
      previewUrl
    });

    return {
      ok: true,
      videoUrl,
      previewUrl,
      provider: videoProviderName,
      requestId: undefined
    };

  } catch (error) {
    logger.error("视频生成失败", {
      provider: videoProviderName,
      error: error instanceof Error ? error.message : String(error)
    });

    return {
      ok: false,
      provider: videoProviderName,
      requestId: undefined,
      message: "视频生成失败",
      error: error instanceof Error ? error.message : String(error)
    };
  }
}
