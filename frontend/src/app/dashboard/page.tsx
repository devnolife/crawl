import { auth, signOut } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getGitHubData } from "@/lib/github";
import Link from "next/link";
import { SyncButton } from "@/components/dashboard/sync-button";
import { ProjectCard } from "@/components/dashboard/project-card";
import { SkillsSection } from "@/components/dashboard/skills-section";
import { AnalysisButton } from "@/components/dashboard/analysis-button";

export default async function DashboardPage() {
    const session = await auth();

    if (!session?.user) {
        redirect("/login");
    }

    const githubData = await getGitHubData(session.user.id);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Header */}
            <header className="border-b border-white/10 backdrop-blur-xl bg-white/5">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                                <svg
                                    className="w-5 h-5 text-white"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                                    />
                                </svg>
                            </div>
                            <span className="text-white font-semibold text-lg">
                                GitHub Portfolio
                            </span>
                        </div>

                        <div className="flex items-center gap-4">
                            {session.user.image && (
                                <img
                                    src={session.user.image}
                                    alt={session.user.name || ""}
                                    className="w-8 h-8 rounded-full ring-2 ring-purple-500/50"
                                />
                            )}
                            <span className="text-gray-300 text-sm hidden sm:block">
                                {session.user.name || session.user.email}
                            </span>
                            <form
                                action={async () => {
                                    "use server";
                                    await signOut({ redirectTo: "/" });
                                }}
                            >
                                <button
                                    type="submit"
                                    className="text-gray-400 hover:text-white text-sm transition-colors"
                                >
                                    Logout
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Welcome section */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">
                        Selamat datang, {session.user.name?.split(" ")[0] || "Developer"}! 👋
                    </h1>
                    <p className="text-gray-400">
                        {githubData
                            ? "Berikut analisis portfolio GitHub Anda"
                            : "Sync data GitHub Anda untuk memulai analisis"}
                    </p>
                </div>

                {/* Stats overview */}
                {githubData && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                        {(() => {
                            const repos = githubData.repos as Array<Record<string, unknown>>;
                            const totalRepos = repos.length;
                            const privateRepos = repos.filter(r => r.private === true).length;
                            const publicRepos = totalRepos - privateRepos;

                            return [
                                {
                                    label: "Total Repos",
                                    value: totalRepos,
                                    icon: "📁",
                                    subLabel: `${publicRepos} public, ${privateRepos} private`
                                },
                                { label: "Followers", value: githubData.followers, icon: "👥" },
                                { label: "Following", value: githubData.following, icon: "➡️" },
                                {
                                    label: "Languages",
                                    value: Object.keys(
                                        githubData.languages as Record<string, number>
                                    ).length,
                                    icon: "💻",
                                },
                            ].map((stat, i) => (
                                <div
                                    key={i}
                                    className="backdrop-blur-xl bg-white/5 rounded-xl border border-white/10 p-4"
                                >
                                    <div className="text-2xl mb-2">{stat.icon}</div>
                                    <div className="text-2xl font-bold text-white">{stat.value}</div>
                                    <div className="text-gray-400 text-sm">{stat.label}</div>
                                    {"subLabel" in stat && stat.subLabel && (
                                        <div className="text-gray-500 text-xs mt-1">{stat.subLabel}</div>
                                    )}
                                </div>
                            ));
                        })()}
                    </div>
                )}

                {/* Action buttons */}
                <div className="flex flex-wrap gap-4 mb-8">
                    <SyncButton hasSynced={!!githubData} />
                    {githubData && <AnalysisButton />}
                </div>

                {/* Content sections */}
                {githubData ? (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Projects section */}
                        <div className="lg:col-span-2">
                            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                                <span>📂</span> Top Projects
                            </h2>
                            <div className="space-y-4">
                                {(githubData.repos as Array<Record<string, unknown>>)
                                    .filter((r) => !r.fork)
                                    .sort(
                                        (a, b) =>
                                            ((b.stargazers_count as number) || 0) -
                                            ((a.stargazers_count as number) || 0)
                                    )
                                    .slice(0, 6)
                                    .map((repo, i) => (
                                        <ProjectCard key={i} repo={repo} />
                                    ))}
                            </div>
                        </div>

                        {/* Skills section */}
                        <div>
                            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                                <span>🎯</span> Skills
                            </h2>
                            <SkillsSection
                                languages={githubData.languages as Record<string, number>}
                            />
                        </div>
                    </div>
                ) : (
                    /* Empty state */
                    <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-12 text-center">
                        <div className="text-6xl mb-4">🔄</div>
                        <h3 className="text-xl font-semibold text-white mb-2">
                            Belum ada data GitHub
                        </h3>
                        <p className="text-gray-400 mb-6">
                            Klik tombol "Sync GitHub" untuk mengambil data repository Anda
                        </p>
                    </div>
                )}
            </main>
        </div>
    );
}
