interface SkillsSectionProps {
    languages: Record<string, number>;
}

export function SkillsSection({ languages }: SkillsSectionProps) {
    if (!languages || Object.keys(languages).length === 0) {
        return (
            <div className="backdrop-blur-xl bg-white/5 rounded-xl border border-white/10 p-6 text-center">
                <p className="text-gray-400">No language data available</p>
            </div>
        );
    }

    // Sort languages by bytes and calculate percentages
    const total = Object.values(languages).reduce((a, b) => a + b, 0);
    const sortedLanguages = Object.entries(languages)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([name, bytes]) => ({
            name,
            bytes,
            percentage: (bytes / total) * 100,
        }));

    // Language colors
    const languageColors: Record<string, string> = {
        JavaScript: "from-yellow-400 to-yellow-600",
        TypeScript: "from-blue-400 to-blue-600",
        Python: "from-green-400 to-green-600",
        Java: "from-orange-400 to-orange-600",
        Go: "from-cyan-400 to-cyan-600",
        Rust: "from-orange-500 to-orange-700",
        Ruby: "from-red-400 to-red-600",
        PHP: "from-purple-400 to-purple-600",
        "C#": "from-green-500 to-green-700",
        "C++": "from-pink-400 to-pink-600",
        C: "from-gray-400 to-gray-600",
        Swift: "from-orange-400 to-orange-600",
        Kotlin: "from-purple-500 to-purple-700",
        Dart: "from-blue-400 to-blue-600",
        HTML: "from-red-400 to-red-600",
        CSS: "from-blue-500 to-blue-700",
        Vue: "from-emerald-400 to-emerald-600",
        Shell: "from-gray-400 to-gray-600",
    };

    const getGradient = (lang: string) =>
        languageColors[lang] || "from-gray-400 to-gray-600";

    return (
        <div className="backdrop-blur-xl bg-white/5 rounded-xl border border-white/10 p-4 space-y-4">
            {sortedLanguages.map((lang, i) => (
                <div key={i}>
                    <div className="flex items-center justify-between mb-1.5">
                        <span className="text-white text-sm font-medium">{lang.name}</span>
                        <span className="text-gray-400 text-xs">
                            {lang.percentage.toFixed(1)}%
                        </span>
                    </div>
                    <div className="w-full bg-gray-700/50 rounded-full h-2">
                        <div
                            className={`bg-gradient-to-r ${getGradient(lang.name)} h-2 rounded-full transition-all duration-500`}
                            style={{ width: `${Math.min(lang.percentage, 100)}%` }}
                        />
                    </div>
                </div>
            ))}
        </div>
    );
}
