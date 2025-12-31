
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

export interface Point {
  x: number;
  y: number;
}

export type GazeZone = 'left' | 'right' | 'out';

export interface GazeInfo {
  zone: GazeZone;
  blinkCount: number;
  isEyesClosed: boolean;
  focusScore: number;
}

export interface BookPage {
  id: number;
  title: string;
  content: string;
}

export interface ConcentrationReport {
  message: string;
  suggestion: string;
  level: 'high' | 'medium' | 'low';
}

// Added BubbleColor and Bubble for Slingshot
export type BubbleColor = 'red' | 'blue' | 'green' | 'yellow' | 'purple' | 'orange';

export interface Bubble {
  id: string;
  row: number;
  col: number;
  x: number;
  y: number;
  color: BubbleColor;
  active: boolean;
}

// Added Particle for Slingshot/Muncher
export interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  color: string;
  size: number;
}

// Added TargetCandidate for Slingshot
export interface TargetCandidate {
  id: string;
  color: BubbleColor;
  size: number;
  row: number;
  col: number;
  pointsPerBubble: number;
  description: string;
}

// Added Treat types for CakeMuncher
export type TreatType = 'cupcake' | 'cookie' | 'donut' | 'icecream' | 'cake' | 'cherry';

export interface Treat {
  id: string;
  x: number;
  y: number;
  type: TreatType;
  active: boolean;
  points: number;
  emoji: string;
  scale: number;
  velocity: number;
}

// Added WordTreat and Quiz for WordMuncher
export interface WordTreat {
  id: string;
  x: number;
  y: number;
  type: TreatType;
  word: string;
  isCorrect: boolean;
  active: boolean;
  velocity: number;
}

export interface Quiz {
  image: string;
  word: string;
  hint: string;
  category: string;
}

export interface DebugInfo {
  latency: number;
  screenshotBase64?: string;
  rawResponse: string;
  timestamp: string;
  parsedResponse?: any;
  promptContext?: string;
  error?: string;
}

export interface AiResponse {
  report?: ConcentrationReport;
  hint?: any;
  debug: DebugInfo;
}

declare global {
  interface Window {
    FaceMesh: any;
    Camera: any;
    // Added MediaPipe Hands and drawing utils to Window interface
    Hands: any;
    drawConnectors: any;
    drawLandmarks: any;
    HAND_CONNECTIONS: any;
  }
}
