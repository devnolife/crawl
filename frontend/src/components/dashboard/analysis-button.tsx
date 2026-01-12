"use client";

import { useState } from "react";

interface AnalysisResult {
    skill_analysis?: {
        top_skills: Array<{ name: string; score: number; percentage: number }>;
        experience_level: string;
        specialization: string;
        strength_score: number;
    };
    cv_recommendations?: {
        summary: string;
        highlight_projects: Array<{
            name: string;
            description: string;
            language: string;
            stars: number;
        }>;
        improvement_suggestions: string[];
        cv_score: number;
    };
}

export function AnalysisButton() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);

    const handleAnalysis = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch("/api/analysis", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ type: "full" }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || "Analysis failed");
            }

            const data = await response.json();
            setResult(data);
            setShowModal(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Analysis failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <button
                onClick={handleAnalysis}
                disabled={loading}
                className="flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl font-medium transition-all duration-200 border border-white/20 disabled:opacity-50 hover:scale-[1.02]"
            >
                {loading ? (
                    <>
                        <svg
                            className="animate-spin w-5 h-5"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                            />
                            <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                        </svg>
                        Analyzing...
                    </>
                ) : (
                    <>
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                            />
                        </svg>
                        Analyze & Get CV Tips
                    </>
                )}
            </button>

            {error && <p className="text-red-400 text-sm">{error}</p>}

            {/* Analysis Result Modal */}
            {showModal && result && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-slate-800 rounded-2xl border border-white/20 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="p-6 border-b border-white/10 flex items-center justify-between">
                            <h2 className="text-xl font-bold text-white">
                                📊 Analysis Result
                            </h2>
                            <button
                                onClick={() => setShowModal(false)}
                                className="text-gray-400 hover:text-white"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="p-6 space-y-6">
                            {/* Skill Analysis */}
                            {result.skill_analysis && (
                                <div>
                                    <h3 className="text-lg font-semibold text-white mb-4">
                                        🎯 Skill Analysis
                                    </h3>
                                    <div className="grid grid-cols-2 gap-4 mb-4">
                                        <div className="bg-white/5 rounded-xl p-4">
                                            <div className="text-gray-400 text-sm">Experience</div>
                                            <div className="text-white font-semibold capitalize">
                                                {result.skill_analysis.experience_level}
                                            </div>
                                        </div>
                                        <div className="bg-white/5 rounded-xl p-4">
                                            <div className="text-gray-400 text-sm">Specialization</div>
                                            <div className="text-white font-semibold capitalize">
                                                {result.skill_analysis.specialization}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-white/5 rounded-xl p-4 mb-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-gray-400 text-sm">
                                                Overall Strength
                                            </span>
                                            <span className="text-white font-bold">
                                                {result.skill_analysis.strength_score}%
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-700 rounded-full h-3">
                                            <div
                                                className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full"
                                                style={{
                                                    width: `${result.skill_analysis.strength_score}%`,
                                                }}
                                            />
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        {result.skill_analysis.top_skills.slice(0, 5).map((skill, i) => (
                                            <div
                                                key={i}
                                                className="flex items-center justify-between bg-white/5 rounded-lg px-4 py-2"
                                            >
                                                <span className="text-white">{skill.name}</span>
                                                <span className="text-purple-400">
                                                    {skill.percentage.toFixed(0)}%
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* CV Recommendations */}
                            {result.cv_recommendations && (
                                <div>
                                    <h3 className="text-lg font-semibold text-white mb-4">
                                        📝 CV Recommendations
                                    </h3>

                                    <div className="bg-white/5 rounded-xl p-4 mb-4">
                                        <div className="text-gray-400 text-sm mb-2">
                                            Professional Summary
                                        </div>
                                        <p className="text-white">{result.cv_recommendations.summary}</p>
                                    </div>

                                    <div className="bg-white/5 rounded-xl p-4 mb-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-gray-400 text-sm">CV Score</span>
                                            <span className="text-white font-bold">
                                                {result.cv_recommendations.cv_score}%
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-700 rounded-full h-3">
                                            <div
                                                className="bg-gradient-to-r from-green-500 to-emerald-500 h-3 rounded-full"
                                                style={{
                                                    width: `${result.cv_recommendations.cv_score}%`,
                                                }}
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-gray-400 text-sm mb-2">
                                            💡 Improvement Suggestions
                                        </div>
                                        <ul className="space-y-2">
                                            {result.cv_recommendations.improvement_suggestions.map(
                                                (suggestion, i) => (
                                                    <li
                                                        key={i}
                                                        className="flex items-start gap-2 text-white text-sm"
                                                    >
                                                        <span className="text-yellow-400">•</span>
                                                        {suggestion}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
