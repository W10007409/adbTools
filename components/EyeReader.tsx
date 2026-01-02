
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
  title: "AI? ?몃쪟??誘몃옒",
  content: `??${i + 1}?? 吏?μ쓽 吏꾪솕? 湲곗닠???뱀씠??n\n???섏씠吏?먯꽌???멸났吏?μ씠 ?대뼸寃??멸컙???숈뒿 援ъ“瑜?紐⑤갑?섎ŉ 諛쒖쟾???붾뒗吏 ?ㅻ챸?⑸땲?? ?ㅻ떒 ?뺤떇???덉씠?꾩썐???듯빐 媛?낆꽦???믪??쇰ŉ, ?쒖꽑 異붿쟻 湲곗닠??寃고빀?섏뿬 ?낆옄???몄? 遺?섎? ?ㅼ떆媛꾩쑝濡?痢≪젙?????덉뒿?덈떎. ?띿뒪?몄쓽 ?먮쫫???곕씪媛???덈룞?먯쓽 誘몄꽭???吏곸엫? ?곕━媛 ?뺣낫瑜?泥섎━?섎뒗 諛⑹떇??蹂댁뿬二쇰뒗 以묒슂??吏?쒓? ?⑸땲??\n\n湲곗닠??諛쒖쟾? ?댁젣 ?⑥닚???꾧뎄瑜?留뚮뱶???섏????섏뼱, ?곕━??媛먭컖怨??몄? ?λ젰???뺤옣?섎뒗 ?④퀎???대Ⅴ??듬땲?? ??梨낆쓽 ?댁슜???쎌쑝硫??뱀떊???뚭? ?대뼸寃?諛섏쓳?섎뒗吏 ?뺤씤?대낫?몄슂.`
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
      
      // 媛?대뱶???묒? 罹??붾㈃
      canvas.width = 240;
      canvas.height = 180;
      ctx.save();
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);
      ctx.restore();

      if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
        const landmarks = results.multiFaceLandmarks[0];
        
        // ?덈룞???쒕뱶留덊겕 (MediaPipe Iris)
        // ?쇱そ ?덈룞?? 468, ?ㅻⅨ履??덈룞?? 473
        const leftIris = landmarks[468];
        const rightIris = landmarks[473];
        const leftEyeOuter = landmarks[33];
        const leftEyeInner = landmarks[133];

        // ?쒖꽑 ?먮퀎 (?⑥닚?붾맂 濡쒖쭅: Iris??x醫뚰몴 鍮꾩쑉 ?ъ슜)
        const avgIrisX = (leftIris.x + rightIris.x) / 2;
        let zone: GazeZone = 'out';
        
        // 嫄곗슱 紐⑤뱶?대?濡??쒕뱶留덊겕 x醫뚰몴瑜?諛섏쟾?쒖폒 ?앷컖
        if (avgIrisX > 0.4 && avgIrisX < 0.6) {
          // 以묒븰(移대찓?쇰? ?뺣㈃?쇰줈 ?묒떆) -> ?쇱そ ?섏씠吏 ?뱀? ?ㅻⅨ履??섏씠吏 寃곗젙
          // ?ㅼ젣 ?섍꼍?먯꽌???붾㈃怨?移대찓?쇱쓽 媛곷룄 怨꾩궛???꾩슂?섏?留? ?ш린?쒕뒗 ?곕え?⑹쑝濡쏧ris ?명뼢???ъ슜
          const eyeWidth = Math.abs(leftEyeInner.x - leftEyeOuter.x);
          const irisOffset = (leftIris.x - leftEyeOuter.x) / eyeWidth;
          
          if (irisOffset < 0.45) zone = 'right';
          else if (irisOffset > 0.55) zone = 'left';
          else zone = 'left'; // 湲곕낯
        } else {
          zone = 'out';
        }

        setGazeZone(zone);

        // ??媛먯쓬 媛먯? (吏묒쨷???섎씫 ?붿냼)
        const leftUpper = landmarks[159];
        const leftLower = landmarks[145];
        const eyeOpenDist = Math.abs(leftUpper.y - leftLower.y);
        const isClosed = eyeOpenDist < 0.012;

        const currentFocus = isClosed ? 20 : (zone === 'out' ? 50 : 100);
        setFocusScore(prev => prev * 0.9 + currentFocus * 0.1);

        // ?쒖꽑 ?뺣낫 湲곕줉
        gazeHistory.current.push({
          zone,
          blinkCount: 0, // 怨좊룄???꾩슂
          isEyesClosed: isClosed,
          focusScore: currentFocus
        });
        if (gazeHistory.current.length > 100) gazeHistory.current.shift();

        // ?쒓컖???쇰뱶諛?(?덈룞??留덉빱)
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.arc((1 - leftIris.x) * canvas.width, leftIris.y * canvas.height, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc((1 - rightIris.x) * canvas.width, rightIris.y * canvas.height, 3, 0, Math.PI * 2);
        ctx.fill();

        // Gemini AI 遺꾩꽍 ?몃━嫄?(10珥?二쇨린)
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

      {/* ?쇱そ ?ъ씠?쒕컮: AI 紐⑤땲?곕쭅 */}
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
              {report ? `"${report.message}"` : "?낆꽌 ?듦???遺꾩꽍?섍퀬 ?덉뒿?덈떎..."}
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
            <Settings className="w-4 h-4" /> ?ㅼ젙
          </button>
        </div>
      </div>

      {/* 硫붿씤 ?낆꽌 ?곸뿭 */}
      <main className="flex-1 relative flex flex-col items-center justify-center p-12 bg-[#f4f1ea] overflow-hidden">
        {/* ?섏씠吏 而⑦뀒?대꼫: ?묐㈃ 蹂닿린 */}
        <div className="relative flex w-full max-w-6xl aspect-[1.4/1] bg-white shadow-[0_20px_50px_rgba(0,0,0,0.1)] rounded-lg overflow-hidden border border-[#d8d3c9]">
          
          {/* 以묒븰 ?묓옒??*/}
          <div className="absolute inset-y-0 left-1/2 w-px bg-gradient-to-r from-transparent via-black/10 to-transparent z-10" />

          {/* ?쇱そ ?섏씠吏 */}
          <div className={`flex-1 p-16 transition-opacity duration-300 ${gazeZone === 'left' ? 'bg-[#fdfdfd]' : 'opacity-80'}`}>
            <span className="block text-[10px] text-slate-400 font-sans font-bold tracking-widest mb-8 uppercase">Page {DUMMY_PAGES[currentPageIndex].id}</span>
            <h2 className="text-3xl font-bold mb-8 text-slate-800 leading-tight">{DUMMY_PAGES[currentPageIndex].title}</h2>
            <div className="columns-1 gap-8 text-lg leading-[1.8] text-slate-700 whitespace-pre-wrap first-letter:text-5xl first-letter:font-bold first-letter:mr-3 first-letter:float-left first-letter:text-emerald-800">
              {DUMMY_PAGES[currentPageIndex].content}
            </div>
            {gazeZone === 'left' && <div className="mt-8 flex items-center gap-2 text-emerald-500 font-sans text-[10px] font-bold animate-pulse"><Eye className="w-3 h-3" /> READING HERE</div>}
          </div>

          {/* ?ㅻⅨ履??섏씠吏 */}
          <div className={`flex-1 p-16 border-l border-[#f0ede6] transition-opacity duration-300 ${gazeZone === 'right' ? 'bg-[#fdfdfd]' : 'opacity-80'}`}>
            <span className="block text-[10px] text-slate-400 font-sans font-bold tracking-widest mb-8 uppercase">Page {DUMMY_PAGES[currentPageIndex + 1].id}</span>
            <h2 className="text-3xl font-bold mb-8 text-slate-800 leading-tight">{DUMMY_PAGES[currentPageIndex + 1].title}</h2>
            <div className="columns-1 gap-8 text-lg leading-[1.8] text-slate-700 whitespace-pre-wrap">
              {DUMMY_PAGES[currentPageIndex + 1].content}
            </div>
            {gazeZone === 'right' && <div className="mt-8 flex items-center gap-2 text-emerald-500 font-sans text-[10px] font-bold animate-pulse"><Eye className="w-3 h-3" /> READING HERE</div>}
          </div>

          {/* ?섏씠吏 ?댄깉 ?뚮┝ */}
          {gazeZone === 'out' && (
            <div className="absolute inset-0 z-30 bg-black/5 backdrop-blur-[2px] flex items-center justify-center">
              <div className="bg-white/90 px-6 py-3 rounded-full shadow-lg border border-slate-200 flex items-center gap-3 animate-in fade-in zoom-in duration-300">
                <Sparkles className="w-5 h-5 text-orange-400" />
                <span className="text-sm font-sans font-bold text-slate-600">梨낆뿉 吏묒쨷?섎㈃ ?먯닔媛 ?щ씪媛??</span>
              </div>
            </div>
          )}
        </div>

        {/* ?대퉬寃뚯씠??而⑦듃濡?*/}
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

        {/* ?섎떒 ?⑥텞??媛?대뱶 */}
        <div className="absolute bottom-6 flex gap-6 text-[10px] font-sans font-bold text-slate-400 tracking-wider">
          <span className="flex items-center gap-1"><Maximize2 className="w-3 h-3" /> FULLSCREEN: F</span>
          <span className="flex items-center gap-1"><BookOpen className="w-3 h-3" /> THEME: SEP_T</span>
        </div>
      </main>

      {loading && (
        <div className="absolute inset-0 bg-[#fcfaf7] z-[100] flex flex-col items-center justify-center">
          <Loader2 className="w-12 h-12 text-emerald-600 animate-spin mb-4" />
          <p className="text-lg font-bold text-emerald-900 font-sans tracking-tight">AI ?쇱씠釉뚮윭由?濡쒕뵫 以?..</p>
        </div>
      )}
    </div>
  );
};

export default EyeReader;
