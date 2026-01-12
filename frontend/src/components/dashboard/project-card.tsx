interface ProjectCardProps {
    repo: Record<string, unknown>;
}

export function ProjectCard({ repo }: ProjectCardProps) {
    const name = repo.name as string;
    const description = (repo.description as string) || "No description";
    const language = repo.language as string | null;
    const stars = (repo.stargazers_count as number) || 0;
    const forks = (repo.forks_count as number) || 0;
    const url = repo.html_url as string;
    const topics = (repo.topics as string[]) || [];
    const isPrivate = (repo.private as boolean) || false;

    // Language colors
    const languageColors: Record<string, string> = {
        JavaScript: "bg-yellow-400",
        TypeScript: "bg-blue-400",
        Python: "bg-green-400",
        Java: "bg-orange-400",
        Go: "bg-cyan-400",
        Rust: "bg-orange-600",
        Ruby: "bg-red-400",
        PHP: "bg-purple-400",
        "C#": "bg-green-600",
        "C++": "bg-pink-400",
        C: "bg-gray-400",
        Swift: "bg-orange-500",
        Kotlin: "bg-purple-500",
        Dart: "bg-blue-500",
        HTML: "bg-red-500",
        CSS: "bg-blue-600",
        Vue: "bg-emerald-400",
    };

    return (
        <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="block backdrop-blur-xl bg-white/5 rounded-xl border border-white/10 p-4 hover:bg-white/10 transition-all duration-200 hover:scale-[1.01] group"
        >
            <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                    <h3 className="font-medium text-white group-hover:text-purple-400 transition-colors">
                        {name}
                    </h3>
                    {isPrivate && (
                        <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 text-xs rounded-full flex items-center gap-1">
                            🔒 Private
                        </span>
                    )}
                </div>
                <svg
                    className="w-4 h-4 text-gray-500 group-hover:text-gray-300 transition-colors"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                </svg>
            </div>

            <p className="text-gray-400 text-sm mb-3 line-clamp-2">{description}</p>

            <div className="flex items-center gap-4 text-sm">
                {language && (
                    <div className="flex items-center gap-1.5">
                        <div
                            className={`w-3 h-3 rounded-full ${languageColors[language] || "bg-gray-400"
                                }`}
                        />
                        <span className="text-gray-300">{language}</span>
                    </div>
                )}

                <div className="flex items-center gap-1 text-gray-400">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                    <span>{stars}</span>
                </div>

                <div className="flex items-center gap-1 text-gray-400">
                    <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
                        />
                    </svg>
                    <span>{forks}</span>
                </div>
            </div>

            {topics.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-3">
                    {topics.slice(0, 4).map((topic, i) => (
                        <span
                            key={i}
                            className="px-2 py-0.5 bg-purple-500/20 text-purple-300 text-xs rounded-full"
                        >
                            {topic}
                        </span>
                    ))}
                </div>
            )}
        </a>
    );
}
