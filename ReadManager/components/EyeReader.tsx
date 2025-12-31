
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { analyzeConcentration } from '../services/geminiService';
import { GazeInfo, GazeZone, BookPage, ConcentrationReport } from '../types';
import { 
  Loader2, BookOpen, ChevronLeft, ChevronRight, 
  Eye, BrainCircuit, Activity, Sparkles, 
  Maximize2, Settings, Coffee
} from 'lucide-react';

const DUMMY_PAGES: BookPage[] = Array.from({ length: 10 }, (_, i) => ({
  id: i + 1,
  title: "AI와 인류의 미래",
  content: `제 ${i + 1}장: 지능의 진화와 기술적 특이점\n\n이 페이지에서는 인공지능이 어떻게 인간의 학습 구조를 모방하며 발전해 왔는지 설명합니다. 다단 형식의 레이아웃을 통해 가독성을 높였으며, 시선 추적 기술을 결합하여 독자의 인지 부하를 실시간으로 측정할 수 있습니다. 텍스트의 흐름을 따라가는 눈동자의 미세한 움직임은 우리가 정보를 처리하는 방식을 보여주는 중요한 지표가 됩니다.\n\n기술의 발전은 이제 단순히 도구를 만드는 수준을 넘어, 우리의 감각과 인지 능력을 확장하는 단계에 이르렀습니다. 이 책의 내용을 읽으며 당신의 뇌가 어떻게 반응하는지 확인해보세요.`
}));

const EyeReader: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const [loading, setLoading] = useState(true);
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [gazeZone, setGazeZone] = useState<GazeZone>('out');
  const [focusScore, setFocusScore] = useState(100);
  const [report, setReport] = useState<ConcentrationReport | null>(null);
  const [isAiAnalyzing, setIsAiAnalyzing] = useState(false);
  const gazeHistory = useRef<GazeInfo[]>([]);
  const lastAiAnalysisTime = useRef(0);

  const nextPage = () => setCurrentPageIndex(prev => Math.min(prev + 2, DUMMY_PAGES.length - 2));
  const prevPage = () => setCurrentPageIndex(prev => Math.max(prev - 2, 0));

  useEffect(() => {
    if (!videoRef.current || !canvasRef.current || !containerRef.current) return;

    const faceMesh = new window.FaceMesh({
      locateFile: (file: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`,
    });

    faceMesh.setOptions({
      maxNumFaces: 1,
      refineLandmarks: true,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });

    const onResults = (results: any) => {
      setLoading(false);
      const canvas = canvasRef.current!;
      const ctx = canvas.getContext('2d')!;
      
      // 가이드용 작은 캠 화면
      canvas.width = 240;
      canvas.height = 180;
      ctx.save();
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);
      ctx.restore();

      if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
        const landmarks = results.multiFaceLandmarks[0];
        
        // 눈동자 랜드마크 (MediaPipe Iris)
        // 왼쪽 눈동자: 468, 오른쪽 눈동자: 473
        const leftIris = landmarks[468];
        const rightIris = landmarks[473];
        const leftEyeOuter = landmarks[33];
        const leftEyeInner = landmarks[133];

        // 시선 판별 (단순화된 로직: Iris의 x좌표 비율 사용)
        const avgIrisX = (leftIris.x + rightIris.x) / 2;
        let zone: GazeZone = 'out';
        
        // 거울 모드이므로 랜드마크 x좌표를 반전시켜 생각
        if (avgIrisX > 0.4 && avgIrisX < 0.6) {
          // 중앙(카메라를 정면으로 응시) -> 왼쪽 페이지 혹은 오른쪽 페이지 결정
          // 실제 환경에서는 화면과 카메라의 각도 계산이 필요하지만, 여기서는 데모용으로Iris 편향도 사용
          const eyeWidth = Math.abs(leftEyeInner.x - leftEyeOuter.x);
          const irisOffset = (leftIris.x - leftEyeOuter.x) / eyeWidth;
          
          if (irisOffset < 0.45) zone = 'right';
          else if (irisOffset > 0.55) zone = 'left';
          else zone = 'left'; // 기본
        } else {
          zone = 'out';
        }

        setGazeZone(zone);

        // 눈 감음 감지 (집중도 하락 요소)
        const leftUpper = landmarks[159];
        const leftLower = landmarks[145];
        const eyeOpenDist = Math.abs(leftUpper.y - leftLower.y);
        const isClosed = eyeOpenDist < 0.012;

        const currentFocus = isClosed ? 20 : (zone === 'out' ? 50 : 100);
        setFocusScore(prev => prev * 0.9 + currentFocus * 0.1);

        // 시선 정보 기록
        gazeHistory.current.push({
          zone,
          blinkCount: 0, // 고도화 필요
          isEyesClosed: isClosed,
          focusScore: currentFocus
        });
        if (gazeHistory.current.length > 100) gazeHistory.current.shift();

        // 시각적 피드백 (눈동자 마커)
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.arc((1 - leftIris.x) * canvas.width, leftIris.y * canvas.height, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc((1 - rightIris.x) * canvas.width, rightIris.y * canvas.height, 3, 0, Math.PI * 2);
        ctx.fill();

        // Gemini AI 분석 트리거 (10초 주기)
        if (Date.now() - lastAiAnalysisTime.current > 10000) {
          lastAiAnalysisTime.current = Date.now();
          const screenshot = canvas.toDataURL('image/jpeg');
          setIsAiAnalyzing(true);
          analyzeConcentration(screenshot, gazeHistory.current, DUMMY_PAGES[currentPageIndex].title)
            .then(res => {
              setReport(res.report);
              setIsAiAnalyzing(false);
            });
        }
      } else {
        setGazeZone('out');
        setFocusScore(prev => prev * 0.95);
      }
    };

    faceMesh.onResults(onResults);
    const camera = new window.Camera(videoRef.current, {
      onFrame: async () => { if (videoRef.current) await faceMesh.send({ image: videoRef.current }); },
      width: 640, height: 480,
    });
    camera.start();

    return () => { camera.stop(); faceMesh.close(); };
  }, [currentPageIndex]);

  return (
    <div ref={containerRef} className="flex h-screen bg-[#fcfaf7] text-[#2c2c2c] overflow-hidden font-serif">
      <video ref={videoRef} className="hidden" />

      {/* 왼쪽 사이드바: AI 모니터링 */}
      <div className="w-72 bg-white border-r border-[#e8e4de] p-6 flex flex-col gap-6 z-20 shadow-sm">
        <div className="flex items-center gap-3 text-emerald-700">
          <BookOpen className="w-8 h-8" />
          <h1 className="text-xl font-bold font-sans tracking-tight">Eye-Read</h1>
        </div>

        <div className="rounded-2xl overflow-hidden border-2 border-emerald-100 bg-slate-50 relative aspect-video">
          <canvas ref={canvasRef} className="w-full h-full" />
          <div className="absolute top-2 right-2 px-2 py-1 bg-black/60 rounded text-[10px] text-white font-sans flex items-center gap-1">
            <Activity className="w-3 h-3 text-emerald-400" /> LIVE GAZE
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-sans text-slate-500 font-bold">FOCUS SCORE</span>
              <span className={`text-sm font-bold font-sans ${focusScore > 70 ? 'text-emerald-600' : 'text-orange-500'}`}>
                {Math.round(focusScore)}%
              </span>
            </div>
            <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${focusScore > 70 ? 'bg-emerald-500' : 'bg-orange-400'}`}
                style={{ width: `${focusScore}%` }}
              />
            </div>
          </div>

          <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-100 relative overflow-hidden">
            <div className="flex items-center gap-2 mb-2">
              <BrainCircuit className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-sans font-bold text-emerald-700">AI INSIGHT</span>
              {isAiAnalyzing && <Loader2 className="w-3 h-3 animate-spin text-emerald-400 ml-auto" />}
            </div>
            <p className="text-sm leading-snug text-emerald-900 font-sans font-medium">
              {report ? `"${report.message}"` : "독서 습관을 분석하고 있습니다..."}
            </p>
            {report?.suggestion && (
              <div className="mt-2 flex items-start gap-2 text-[11px] text-emerald-700 font-sans border-t border-emerald-200/50 pt-2">
                <Coffee className="w-3 h-3 shrink-0" />
                <span>{report.suggestion}</span>
              </div>
            )}
          </div>
        </div>

        <div className="mt-auto space-y-2">
          <button className="w-full py-2 bg-white border border-slate-200 rounded-lg text-xs font-sans font-bold text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-2">
            <Settings className="w-4 h-4" /> 설정
          </button>
        </div>
      </div>

      {/* 메인 독서 영역 */}
      <main className="flex-1 relative flex flex-col items-center justify-center p-12 bg-[#f4f1ea] overflow-hidden">
        {/* 페이지 컨테이너: 양면 보기 */}
        <div className="relative flex w-full max-w-6xl aspect-[1.4/1] bg-white shadow-[0_20px_50px_rgba(0,0,0,0.1)] rounded-lg overflow-hidden border border-[#d8d3c9]">
          
          {/* 중앙 접힘선 */}
          <div className="absolute inset-y-0 left-1/2 w-px bg-gradient-to-r from-transparent via-black/10 to-transparent z-10" />

          {/* 왼쪽 페이지 */}
          <div className={`flex-1 p-16 transition-opacity duration-300 ${gazeZone === 'left' ? 'bg-[#fdfdfd]' : 'opacity-80'}`}>
            <span className="block text-[10px] text-slate-400 font-sans font-bold tracking-widest mb-8 uppercase">Page {DUMMY_PAGES[currentPageIndex].id}</span>
            <h2 className="text-3xl font-bold mb-8 text-slate-800 leading-tight">{DUMMY_PAGES[currentPageIndex].title}</h2>
            <div className="columns-1 gap-8 text-lg leading-[1.8] text-slate-700 whitespace-pre-wrap first-letter:text-5xl first-letter:font-bold first-letter:mr-3 first-letter:float-left first-letter:text-emerald-800">
              {DUMMY_PAGES[currentPageIndex].content}
            </div>
            {gazeZone === 'left' && <div className="mt-8 flex items-center gap-2 text-emerald-500 font-sans text-[10px] font-bold animate-pulse"><Eye className="w-3 h-3" /> READING HERE</div>}
          </div>

          {/* 오른쪽 페이지 */}
          <div className={`flex-1 p-16 border-l border-[#f0ede6] transition-opacity duration-300 ${gazeZone === 'right' ? 'bg-[#fdfdfd]' : 'opacity-80'}`}>
            <span className="block text-[10px] text-slate-400 font-sans font-bold tracking-widest mb-8 uppercase">Page {DUMMY_PAGES[currentPageIndex + 1].id}</span>
            <h2 className="text-3xl font-bold mb-8 text-slate-800 leading-tight">{DUMMY_PAGES[currentPageIndex + 1].title}</h2>
            <div className="columns-1 gap-8 text-lg leading-[1.8] text-slate-700 whitespace-pre-wrap">
              {DUMMY_PAGES[currentPageIndex + 1].content}
            </div>
            {gazeZone === 'right' && <div className="mt-8 flex items-center gap-2 text-emerald-500 font-sans text-[10px] font-bold animate-pulse"><Eye className="w-3 h-3" /> READING HERE</div>}
          </div>

          {/* 페이지 이탈 알림 */}
          {gazeZone === 'out' && (
            <div className="absolute inset-0 z-30 bg-black/5 backdrop-blur-[2px] flex items-center justify-center">
              <div className="bg-white/90 px-6 py-3 rounded-full shadow-lg border border-slate-200 flex items-center gap-3 animate-in fade-in zoom-in duration-300">
                <Sparkles className="w-5 h-5 text-orange-400" />
                <span className="text-sm font-sans font-bold text-slate-600">책에 집중하면 점수가 올라가요!</span>
              </div>
            </div>
          )}
        </div>

        {/* 내비게이션 컨트롤 */}
        <div className="mt-12 flex items-center gap-8">
          <button 
            onClick={prevPage}
            disabled={currentPageIndex === 0}
            className="p-4 rounded-full bg-white border border-slate-200 shadow-sm hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <ChevronLeft className="w-6 h-6 text-slate-600" />
          </button>
          
          <div className="px-6 py-2 bg-slate-800 rounded-full text-white text-xs font-sans font-bold tracking-widest">
            {currentPageIndex + 1}-{currentPageIndex + 2} / {DUMMY_PAGES.length}
          </div>

          <button 
            onClick={nextPage}
            disabled={currentPageIndex >= DUMMY_PAGES.length - 2}
            className="p-4 rounded-full bg-white border border-slate-200 shadow-sm hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <ChevronRight className="w-6 h-6 text-slate-600" />
          </button>
        </div>

        {/* 하단 단축키 가이드 */}
        <div className="absolute bottom-6 flex gap-6 text-[10px] font-sans font-bold text-slate-400 tracking-wider">
          <span className="flex items-center gap-1"><Maximize2 className="w-3 h-3" /> FULLSCREEN: F</span>
          <span className="flex items-center gap-1"><BookOpen className="w-3 h-3" /> THEME: SEP_T</span>
        </div>
      </main>

      {loading && (
        <div className="absolute inset-0 bg-[#fcfaf7] z-[100] flex flex-col items-center justify-center">
          <Loader2 className="w-12 h-12 text-emerald-600 animate-spin mb-4" />
          <p className="text-lg font-bold text-emerald-900 font-sans tracking-tight">AI 라이브러리 로딩 중...</p>
        </div>
      )}
    </div>
  );
};

export default EyeReader;
