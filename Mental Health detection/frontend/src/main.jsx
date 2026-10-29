import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { Activity, ArrowRight, Check, LoaderCircle, RotateCcw, ShieldCheck, Sparkles } from "lucide-react";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const countries = ["Australia", "Canada", "France", "Germany", "India", "Mexico", "Other", "Turkey", "UK", "USA"];
const platforms = ["Facebook", "Instagram", "KakaoTalk", "LINE", "LinkedIn", "Snapchat", "TikTok", "Twitter", "VKontakte", "WeChat", "WhatsApp", "YouTube"];

const initialForm = {
  age: 21, gender: "Female", country: "India", academic_level: "Undergraduate",
  most_used_platform: "Instagram", purpose_of_use: "Education", avg_daily_usage_hours: 4,
  daily_unlocks: 120, study_hours: 4, physical_activity_hours: 1.5,
  sleep_hours_per_night: 7, stress_level: "Medium",
};

function Field({ label, name, value, onChange, children, type = "number", min, max, step = "any" }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-ink/80">{label}</span>
      {children || (
        <input className="field" name={name} type={type} value={value} onChange={onChange} required min={min} max={max} step={step} />
      )}
    </label>
  );
}

function Select({ name, value, onChange, options }) {
  return <select className="field" name={name} value={value} onChange={onChange} required>{options.map((option) => <option key={option}>{option}</option>)}</select>;
}

function App() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = Object.fromEntries(Object.entries(form).map(([key, value]) => (
        ["age", "daily_unlocks"].includes(key) ? [key, Number.parseInt(value, 10)] :
          ["avg_daily_usage_hours", "study_hours", "physical_activity_hours", "sleep_hours_per_night"].includes(key) ? [key, Number.parseFloat(value)] : [key, value]
      )));
      const response = await fetch(`${API_URL}/predict`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "The prediction service returned an error.");
      setResult(body);
    } catch (requestError) {
      setError(requestError.message || "Unable to reach the prediction service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-sand text-ink">
      <div className="mx-auto max-w-6xl px-5 py-6 sm:px-8 sm:py-10">
        <nav className="mb-14 flex items-center justify-between">
          <div className="flex items-center gap-2 font-semibold tracking-tight"><span className="rounded-xl bg-moss p-2 text-white"><Activity size={18} /></span> Mindful Measure</div>
          <div className="hidden items-center gap-2 text-sm text-ink/60 sm:flex"><ShieldCheck size={16} /> Private by design</div>
        </nav>
        <section className="mb-12 max-w-3xl">
          <p className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.18em] text-moss"><Sparkles size={16} /> A moment to check in</p>
          <h1 className="font-display text-5xl leading-[1.05] tracking-tight sm:text-7xl">Understand your <em className="text-moss">mental wellness</em> signals.</h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-ink/65">Share a few everyday patterns and receive a model-estimated mental health score for reflection.</p>
        </section>

        <div className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
          <form onSubmit={submit} className="rounded-3xl border border-ink/10 bg-white/80 p-6 shadow-sm sm:p-9">
            <div className="mb-8 flex items-center justify-between border-b border-ink/10 pb-5"><div><h2 className="text-xl font-semibold">Your daily snapshot</h2><p className="mt-1 text-sm text-ink/55">All fields are used by the trained model.</p></div><span className="rounded-full bg-mint px-3 py-1 text-xs font-medium text-moss">12 inputs</span></div>
            <div className="grid gap-5 sm:grid-cols-2">
              <Field label="Age" name="age" value={form.age} onChange={update} min="1" max="120" step="1" />
              <Field label="Gender"><Select name="gender" value={form.gender} onChange={update} options={["Female", "Male"]} /></Field>
              <Field label="Country"><Select name="country" value={form.country} onChange={update} options={countries} /></Field>
              <Field label="Academic level"><Select name="academic_level" value={form.academic_level} onChange={update} options={["Graduate", "High School", "Undergraduate"]} /></Field>
              <Field label="Most used platform"><Select name="most_used_platform" value={form.most_used_platform} onChange={update} options={platforms} /></Field>
              <Field label="Primary purpose"><Select name="purpose_of_use" value={form.purpose_of_use} onChange={update} options={["Education", "Entertainment", "Networking", "News"]} /></Field>
              <Field label="Average daily usage (hours)" name="avg_daily_usage_hours" value={form.avg_daily_usage_hours} onChange={update} min="0" max="24" />
              <Field label="Daily unlocks" name="daily_unlocks" value={form.daily_unlocks} onChange={update} min="0" max="10000" step="1" />
              <Field label="Study hours (daily)" name="study_hours" value={form.study_hours} onChange={update} min="0" max="24" />
              <Field label="Physical activity (hours)" name="physical_activity_hours" value={form.physical_activity_hours} onChange={update} min="0" max="24" />
              <Field label="Sleep per night (hours)" name="sleep_hours_per_night" value={form.sleep_hours_per_night} onChange={update} min="0" max="24" />
              <Field label="Current stress level"><Select name="stress_level" value={form.stress_level} onChange={update} options={["Low", "Medium", "High", "Very High"]} /></Field>
            </div>
            {error && <p role="alert" className="mt-6 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</p>}
            <button disabled={loading} className="mt-8 flex w-full items-center justify-center gap-2 rounded-2xl bg-moss px-5 py-4 font-semibold text-white transition hover:bg-ink disabled:cursor-wait disabled:opacity-70">{loading ? <><LoaderCircle className="animate-spin" size={18} /> Calculating...</> : <>See my score <ArrowRight size={18} /></>}</button>
          </form>

          <aside className="flex flex-col gap-5">
            <div className="rounded-3xl bg-sage p-7"><p className="mb-12 text-sm font-semibold uppercase tracking-[0.16em] text-moss">Your result</p>{result ? <><div className="flex items-end gap-2"><span className="font-display text-7xl leading-none">{result.score.toFixed(2)}</span><span className="mb-1 text-ink/60">score</span></div><div className="mt-7 flex items-start gap-3 border-t border-ink/10 pt-5 text-sm leading-6 text-ink/70"><Check className="mt-1 shrink-0 text-moss" size={17} />{result.interpretation}</div><button onClick={() => setResult(null)} className="mt-7 flex items-center gap-2 text-sm font-semibold text-moss hover:text-ink"><RotateCcw size={15} /> Start over</button></> : <div className="flex min-h-48 items-end"><p className="max-w-xs font-display text-3xl leading-tight text-ink/70">Your reflection will appear here after you complete the check-in.</p></div>}</div>
            <div className="rounded-3xl border border-ink/10 bg-white/60 p-7"><h3 className="font-semibold">A gentle reminder</h3><p className="mt-3 text-sm leading-6 text-ink/60">This tool is informational only. It is not a clinical diagnosis or a substitute for professional mental health care. If you are concerned about your wellbeing, consider speaking with a qualified professional.</p></div>
          </aside>
        </div>
        <footer className="mt-12 border-t border-ink/10 pt-5 text-xs leading-5 text-ink/50">Your responses are sent to the configured prediction API to calculate this result and are not stored by this frontend.</footer>
      </div>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<React.StrictMode><App /></React.StrictMode>);
