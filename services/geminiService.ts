
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import { GoogleGenAI, Modality } from "@google/genai";
import { AiResponse, GazeInfo, TargetCandidate, Quiz, Treat } from "../types";

const MODEL_NAME = "gemini-3-flash-preview";

// Fix: Correct initialization to use named parameter and process.env.API_KEY
const getAiClient = () => new GoogleGenAI({ apiKey: process.env.API_KEY });

/**
 * Analyzes reader concentration based on image and gaze data.
 */
export const analyzeConcentration = async (
  imageBase64: string,
  gazeHistory: GazeInfo[],
  pageTitle: string
): Promise<AiResponse> => {
  const startTime = performance.now();
  const ai = getAiClient();

  const avgFocus = gazeHistory.reduce((acc, curr) => acc + curr.focusScore, 0) / (gazeHistory.length || 1);
  const outCount = gazeHistory.filter(g => g.zone === 'out').length;

  const prompt = `
    ?뱀떊? ?숈뒿 蹂댁“ AI 'Gemini Read-Buddy'?낅땲?? 
    ?ъ슜?먭? '${pageTitle}' ?꾩꽌瑜??쎄퀬 ?덈뒗 紐⑥뒿怨??쒖꽑 ?곗씠?곕? 遺꾩꽍?댁＜?몄슂.
    
    ### ?쒓퀎???곗씠???붿빟 (理쒓렐 10珥?:
    - ?됯퇏 吏묒쨷???먯닔: ${avgFocus.toFixed(1)}/100
    - ?붾㈃ ?댄깉 ?잛닔: ${outCount}??    
    ### 遺꾩꽍 ?붿껌:
    1. ?대?吏 ???ъ슜?먯쓽 ?쒖젙(議몄쓬, 吏猷⑦븿, ?댁쨷 ?????뚯븙?섏꽭??
    2. ?곗씠?곗? ?쒖젙??醫낇빀?섏뿬 吏묒쨷??由ы룷?몃? ?묒꽦?섏꽭??
    
    ### 異쒕젰 ?뺤떇 (JSON):
    {
      "message": "?ъ슜?먯뿉寃?嫄대꽟 ?쒕쭏??,
      "suggestion": "議곗뼵",
      "level": "high" | "medium" | "low"
    }
  `;

  try {
    const cleanBase64 = imageBase64.replace(/^data:image\/(png|jpeg|jpg);base64,/, "");
    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: [
        { text: prompt },
        { inlineData: { mimeType: "image/jpeg", data: cleanBase64 } }
      ],
      config: {
        responseMimeType: "application/json" 
      }
    });

    const endTime = performance.now();
    const text = response.text || "{}";
    const report = JSON.parse(text);

    return {
        report,
        debug: {
            latency: Math.round(endTime - startTime),
            screenshotBase64: imageBase64,
            rawResponse: text,
            timestamp: new Date().toLocaleTimeString()
        }
    };
  } catch (error: any) {
    return {
        report: { message: "吏묒쨷?μ쓣 痢≪젙 以묒엯?덈떎...", suggestion: "?몄븞?섍쾶 ?쎌뼱二쇱꽭??", level: "medium" },
        debug: { latency: 0, rawResponse: error.message, timestamp: "" }
    };
  }
};

/**
 * Provides strategic advice for the Slingshot game.
 */
export const getStrategicHint = async (
  screenshot: string,
  allClusters: TargetCandidate[],
  maxRow: number
) => {
  const startTime = performance.now();
  const ai = getAiClient();
  const prompt = `Analyze this bubble shooter game state.
    Clusters: ${JSON.stringify(allClusters)}
    Max row: ${maxRow}
    
    Recommend a target row and col for high score. Return JSON.
    {
      "message": "Strategic advice",
      "rationale": "Why this move",
      "targetRow": number,
      "targetCol": number,
      "recommendedColor": "red" | "blue" | "green" | "yellow" | "purple" | "orange"
    }`;

  try {
    const cleanBase64 = screenshot.split(',')[1];
    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: [
        { text: prompt },
        { inlineData: { mimeType: "image/jpeg", data: cleanBase64 } }
      ],
      config: { responseMimeType: "application/json" }
    });

    const text = response.text || "{}";
    const parsed = JSON.parse(text);
    const endTime = performance.now();

    return {
      hint: parsed,
      debug: {
        latency: Math.round(endTime - startTime),
        screenshotBase64: screenshot,
        rawResponse: text,
        parsedResponse: parsed,
        promptContext: prompt,
        timestamp: new Date().toLocaleTimeString()
      }
    };
  } catch (error: any) {
    return {
      hint: { message: "Analyzing state...", targetRow: null, targetCol: null },
      debug: { latency: 0, rawResponse: error.message, timestamp: "" }
    };
  }
};

/**
 * Provides gourmet advice for the CakeMuncher game.
 */
export const getGourmetAdvice = async (
  screenshot: string,
  treats: Treat[]
) => {
  const startTime = performance.now();
  const ai = getAiClient();
  const prompt = `You are a Gourmet Chef Coach.
    Treats visible: ${JSON.stringify(treats.filter(t => t.active).map(t => t.type))}
    
    Give a witty munching advice. Return JSON.
    {
      "message": "Short advice",
      "rationale": "Reason"
    }`;

  try {
    const cleanBase64 = screenshot.split(',')[1];
    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: [
        { text: prompt },
        { inlineData: { mimeType: "image/jpeg", data: cleanBase64 } }
      ],
      config: { responseMimeType: "application/json" }
    });

    const text = response.text || "{}";
    const parsed = JSON.parse(text);
    const endTime = performance.now();

    return {
      hint: parsed,
      debug: {
        latency: Math.round(endTime - startTime),
        screenshotBase64: screenshot,
        rawResponse: text,
        timestamp: new Date().toLocaleTimeString()
      }
    };
  } catch (error: any) {
    return {
      hint: { message: "Keep munching!" },
      debug: { latency: 0, rawResponse: error.message, timestamp: "" }
    };
  }
};

/**
 * Provides study buddy advice for WordMuncher.
 */
export const getStudyBuddyAdvice = async (
  screenshot: string,
  quiz: Quiz,
  score: number
) => {
  const startTime = performance.now();
  const ai = getAiClient();
  const prompt = `You are an English Study Buddy.
    Current Quiz: ${quiz.word} (${quiz.hint})
    Score: ${score}
    
    Give encouraging advice and a word fact. Return JSON.
    {
      "message": "Encouragement",
      "explanation": "Fact about the word"
    }`;

  try {
    const cleanBase64 = screenshot.split(',')[1];
    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: [
        { text: prompt },
        { inlineData: { mimeType: "image/jpeg", data: cleanBase64 } }
      ],
      config: { responseMimeType: "application/json" }
    });

    const text = response.text || "{}";
    const parsed = JSON.parse(text);
    const endTime = performance.now();

    return {
      hint: parsed,
      debug: {
        latency: Math.round(endTime - startTime),
        screenshotBase64: screenshot,
        rawResponse: text,
        timestamp: new Date().toLocaleTimeString()
      }
    };
  } catch (error: any) {
    return {
      hint: { message: "Find the word!" },
      debug: { latency: 0, rawResponse: error.message, timestamp: "" }
    };
  }
};

/**
 * Speaks a word using Gemini TTS.
 */
export const speakWord = async (word: string): Promise<string | null> => {
  const ai = getAiClient();
  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-preview-tts",
      contents: [{ parts: [{ text: `Pronounce clearly: ${word}` }] }],
      config: {
        responseModalities: [Modality.AUDIO],
        speechConfig: {
            voiceConfig: {
              prebuiltVoiceConfig: { voiceName: 'Kore' },
            },
        },
      },
    });
    return response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data || null;
  } catch (e) {
    console.error("TTS failed", e);
    return null;
  }
};
