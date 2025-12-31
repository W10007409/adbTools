
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
    당신은 학습 보조 AI 'Gemini Read-Buddy'입니다. 
    사용자가 '${pageTitle}' 도서를 읽고 있는 모습과 시선 데이터를 분석해주세요.
    
    ### 시계열 데이터 요약 (최근 10초):
    - 평균 집중도 점수: ${avgFocus.toFixed(1)}/100
    - 화면 이탈 횟수: ${outCount}회
    
    ### 분석 요청:
    1. 이미지 속 사용자의 표정(졸음, 지루함, 열중 등)을 파악하세요.
    2. 데이터와 표정을 종합하여 집중도 리포트를 작성하세요.
    
    ### 출력 형식 (JSON):
    {
      "message": "사용자에게 건넬 한마디",
      "suggestion": "조언",
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
        report: { message: "집중력을 측정 중입니다...", suggestion: "편안하게 읽어주세요.", level: "medium" },
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
