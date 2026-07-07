import './theme.css';
import { useEffect, useState } from 'react';
import Chatbot from "./Components/Chatbot";
import GoalBreakdown from "./Components/GoalBreakdown";
import HabitLogger from "./Components/HabitLogger";
import IndiaMap from "./Components/India-map/IndiaMap";
import StatePopup from "./Components/India-map/StatePopup";

const NAV_ITEMS = [
  { label: 'Goals',     icon: '🎯', view: 'goals'     },
  { label: 'Habits',    icon: '📊', view: 'habits'    },
  { label: 'Curations', icon: '✨', view: 'curations' },
  { label: 'Socialize', icon: '🤝', view: 'socialize' },
];

const SIMPLE_VIEW_CLS = [
  'w-[min(100%,900px)] mx-auto mt-20 p-6',
  'rounded-[1.25rem] border border-white/10',
  'bg-white/[0.04] backdrop-blur-[16px]',
].join(' ');

function App() {
  const [messages, setMessages] = useState([]);
  const [currentView, setCurrentView] = useState('chat');
  const [selectedState, setSelectedState] = useState(null);

  useEffect(() => {
    const onKeyDown = (e) => { if (e.key === 'Escape') setSelectedState(null); };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const renderCurrentView = () => {
    switch (currentView) {
      case 'goals':     return <GoalBreakdown onBack={() => setCurrentView('chat')} />;
      case 'habits':    return <HabitLogger onBack={() => setCurrentView('chat')} />;
      case 'curations': return <div className={SIMPLE_VIEW_CLS}>Curations</div>;
      case 'socialize': return <div className={SIMPLE_VIEW_CLS}>Socialize</div>;
      default:          return <Chatbot messages={messages} setMessages={setMessages} />;
    }
  };

  return (
    <div className="min-h-screen grid grid-cols-[minmax(300px,38vw)_minmax(0,1fr)] bg-[linear-gradient(180deg,rgba(255,255,255,0.02),transparent_30%)] max-[1100px]:grid-cols-[minmax(280px,44vw)_minmax(0,1fr)] max-[900px]:grid-cols-[1fr]">

      {/* ── Left sidebar ── */}
      <aside className="sticky top-0 h-screen flex flex-col items-center gap-4 px-4 pt-[1.4rem] pb-4 box-border border-r border-blue-400/25 bg-[linear-gradient(180deg,rgba(17,17,17,0.96),rgba(10,10,12,0.98))] shadow-[inset_-1px_0_0_rgba(255,255,255,0.03)] max-[900px]:relative max-[900px]:h-auto max-[900px]:min-h-[52vh] max-[900px]:border-r-0 max-[900px]:border-b max-[900px]:border-blue-400/20 max-[640px]:min-h-[46vh] max-[640px]:px-3">

        <div className="w-full text-center font-extrabold uppercase tracking-[0.12em] text-[#3f7cff] text-[clamp(1.5rem,2vw,2.2rem)] max-[640px]:tracking-[0.08em]">
          INDIAN-AI
        </div>

        <div className="flex-1 w-full flex items-center justify-center py-2 box-border *:w-full *:max-w-full max-[900px]:max-w-105 max-[900px]:mx-auto max-[640px]:max-w-90">
          <IndiaMap selected={selectedState} onSelect={setSelectedState} />
        </div>
      </aside>

      {/* ── Right panel — position:relative so nav can float absolute inside ── */}
      <div className="relative min-w-0 min-h-screen max-[900px]:min-h-0 bg-transparent">

        {/* Navbar — absolute top-right, floats over content */}
        <nav className="absolute top-4 right-4 z-10 flex items-center gap-[0.9rem] max-[900px]:hidden">
          {NAV_ITEMS.map(({ label, icon, view }) => (
            <button
              key={view}
              onClick={() => setCurrentView(view)}
              className={[
                'inline-flex items-center gap-[0.45rem]',
                'py-[0.55rem] px-5 rounded-full border',
                'text-[0.88rem] font-bold cursor-pointer backdrop-blur-lg',
                'transition-[transform,background,border-color,box-shadow] duration-180',
                'hover:-translate-y-0.5 hover:border-white/25 hover:shadow-[0_10px_28px_rgba(0,0,0,0.28)]',
                currentView === view
                  ? 'bg-white/12 border-white/18 text-white'
                  : 'bg-white/7 border-white/7 text-white hover:text-white/80 hover:bg-white/7',
              ].join(' ')}
            >
              {icon} {label}
            </button>
          ))}
        </nav>

        {/* Main content — fills the full right panel */}
        <main className="relative w-full h-full min-h-screen flex items-stretch justify-center p-[1.1rem_1.1rem_1.4rem] box-border [background:linear-gradient(180deg,rgba(255,255,255,0.03),transparent_22%),rgba(0,0,0,0.18)] max-[900px]:min-h-0">
          {renderCurrentView()}
        </main>

        <nav className="hidden max-[900px]:flex w-full flex-nowrap items-center justify-center gap-1 px-3 pb-3 pt-2 overflow-x-hidden bg-[linear-gradient(180deg,rgba(17,17,17,0),rgba(17,17,17,0.82)_30%)]">
          {NAV_ITEMS.map(({ label, icon, view }) => (
            <button
              key={view}
              onClick={() => setCurrentView(view)}
              className={[
                'inline-flex items-center justify-center gap-[0.3rem] flex-1 min-w-0',
                'min-h-11 px-2.5 py-2 rounded-full border text-[0.72rem] font-bold cursor-pointer backdrop-blur-lg',
                'transition-[transform,background,border-color,box-shadow] duration-180',
                currentView === view
                  ? 'bg-white/12 border-white/18 text-white'
                  : 'bg-white/7 border-white/7 text-white hover:text-white/80 hover:bg-white/7',
              ].join(' ')}
            >
              {icon} {label}
            </button>
          ))}
        </nav>
      </div>

      <StatePopup stateName={selectedState} onClose={() => setSelectedState(null)} />
    </div>
  );
}

export default App;