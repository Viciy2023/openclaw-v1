import type { ClawMateConfig, Logger } from "./types";

export interface GenerateImageFastOptions {
  config: ClawMateConfig;
  prompt: string;
  n?: number;
  size?: string;
  logger: Logger;
}

export interface GenerateImageFastResult {
  ok: true;
  provider: string;
  imageUrl: string;
  prompt: string;
  requestId: string | null;
}

export interface GenerateImageFastFailure {
  ok: false;
  provider: string | null;
  requestId: string | null;
  message: string;
  error: string;
}

export type GenerateImageFastResponse = GenerateImageFastResult | GenerateImageFastFailure;

/**
 * 纯文本生图（无参考图）
 * 使用 grok-imagine-1.0-fast 模型
 */
export async function generateImageFast(options: GenerateImageFastOptions): Promise<GenerateImageFastResponse> {
  const { config, prompt, n = 1, size = "1024x1024", logger } = options;

  // 获取 fastProvider 配置
  const fastProviderName = config.fastProvider || config.defaultProvider;
  const providerConfig = config.providers[fastProviderName];

  if (!providerConfig) {
    return {
      ok: false,
      provider: null,
      requestId: null,
      message: "Fast provider not configured",
      error: `Provider "${fastProviderName}" not found in config`,
    };
  }

  logger.info("开始纯文本生图", {
    provider: fastProviderName,
    prompt: prompt.slice(0, 100),
    n,
    size,
  });

  try {
    const baseUrl = (providerConfig.baseUrl as string) || "";
    const apiKey = (providerConfig.apiKey as string) || "";
    const model = (providerConfig.model as string); // 从配置读取模型，不使用硬编码默认值

    if (!model) {
      return {
        ok: false,
        provider: null,
        requestId: null,
        message: "Model not configured",
        error: `Provider "${fastProviderName}" missing model configuration`,
      };
    }

    // 调用 OpenAI-compatible 图片生成接口
    const response = await fetch(`${baseUrl}/images/generations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        prompt,
        n,
        size,
        response_format: "url",
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      logger.error("图片生成API调用失败", {
        provider: fastProviderName,
        status: response.status,
        error: errorText,
      });

      return {
        ok: false,
        provider: fastProviderName,
        requestId: null,
        message: "图片生成失败",
        error: `HTTP ${response.status}: ${errorText}`,
      };
    }

    const result = await response.json();

    // 检查响应格式
    if (result.data && Array.isArray(result.data) && result.data.length > 0) {
      const imageUrl = result.data[0].url;
      const requestId = result.data[0].request_id || null;

      logger.info("纯文本生图成功", {
        provider: fastProviderName,
        imageUrl: imageUrl.slice(0, 100),
        requestId,
      });

      return {
        ok: true,
        provider: fastProviderName,
        imageUrl,
        prompt,
        requestId,
      };
    }

    // 响应格式不符合预期
    logger.error("图片生成响应格式错误", {
      provider: fastProviderName,
      response: JSON.stringify(result).slice(0, 500),
    });

    return {
      ok: false,
      provider: fastProviderName,
      requestId: null,
      message: "图片生成失败",
      error: "Invalid response format from image generation API",
    };
  } catch (error) {
    logger.error("纯文本生图异常", {
      provider: fastProviderName,
      error: error instanceof Error ? error.message : String(error),
    });

    return {
      ok: false,
      provider: fastProviderName,
      requestId: null,
      message: "图片生成失败",
      error: error instanceof Error ? error.message : String(error),
    };
  }
}
