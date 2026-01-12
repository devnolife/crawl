/**
 * GitHub API Service
 * Fetches user data, repositories, and languages from GitHub
 */

import { prisma } from "@/lib/prisma";

const GITHUB_API_URL = "https://api.github.com";

interface GitHubUser {
    login: string;
    avatar_url: string;
    bio: string | null;
    public_repos: number;
    followers: number;
    following: number;
}

interface GitHubRepo {
    id: number;
    name: string;
    full_name: string;
    description: string | null;
    html_url: string;
    language: string | null;
    stargazers_count: number;
    forks_count: number;
    topics: string[];
    fork: boolean;
    archived: boolean;
    created_at: string;
    updated_at: string;
    pushed_at: string;
}

export class GitHubService {
    private accessToken: string;
    private headers: HeadersInit;

    constructor(accessToken: string) {
        this.accessToken = accessToken;
        this.headers = {
            Authorization: `Bearer ${accessToken}`,
            Accept: "application/vnd.github.v3+json",
        };
    }

    /**
     * Fetch authenticated user profile
     */
    async getUser(): Promise<GitHubUser> {
        const response = await fetch(`${GITHUB_API_URL}/user`, {
            headers: this.headers,
        });

        if (!response.ok) {
            throw new Error(`GitHub API error: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Fetch all repositories for the authenticated user
     */
    async getRepositories(perPage: number = 100): Promise<GitHubRepo[]> {
        const repos: GitHubRepo[] = [];
        let page = 1;

        while (true) {
            const response = await fetch(
                `${GITHUB_API_URL}/user/repos?per_page=${perPage}&page=${page}&sort=updated`,
                { headers: this.headers }
            );

            if (!response.ok) {
                throw new Error(`GitHub API error: ${response.statusText}`);
            }

            const pageRepos = await response.json();
            if (pageRepos.length === 0) break;

            repos.push(...pageRepos);
            page++;

            // Safety limit
            if (page > 10) break;
        }

        return repos;
    }

    /**
     * Get language breakdown for a repository
     */
    async getRepoLanguages(repoFullName: string): Promise<Record<string, number>> {
        const response = await fetch(
            `${GITHUB_API_URL}/repos/${repoFullName}/languages`,
            { headers: this.headers }
        );

        if (!response.ok) {
            return {};
        }

        return response.json();
    }

    /**
     * Aggregate languages across all repositories
     */
    async getAggregatedLanguages(repos: GitHubRepo[]): Promise<Record<string, number>> {
        const aggregated: Record<string, number> = {};

        // Limit to avoid rate limiting
        const reposToCheck = repos.slice(0, 30);

        for (const repo of reposToCheck) {
            const languages = await this.getRepoLanguages(repo.full_name);
            for (const [lang, bytes] of Object.entries(languages)) {
                aggregated[lang] = (aggregated[lang] || 0) + bytes;
            }
        }

        return aggregated;
    }

    /**
     * Get contribution statistics
     */
    async getContributionStats(username: string): Promise<Record<string, unknown>> {
        // GitHub doesn't have a direct API for contribution graph
        // We'll use repository stats as a proxy
        const response = await fetch(
            `${GITHUB_API_URL}/users/${username}/events?per_page=100`,
            { headers: this.headers }
        );

        if (!response.ok) {
            return {};
        }

        const events = await response.json();

        // Count event types
        const stats: Record<string, number> = {};
        for (const event of events) {
            const type = event.type;
            stats[type] = (stats[type] || 0) + 1;
        }

        return {
            recentEvents: stats,
            totalRecentActivity: events.length,
        };
    }

    /**
     * Sync all GitHub data for a user
     */
    async syncAllData(userId: string): Promise<void> {
        const user = await this.getUser();
        const repos = await this.getRepositories();
        const languages = await this.getAggregatedLanguages(repos);
        const contributions = await this.getContributionStats(user.login);

        // Upsert GitHub data
        await prisma.githubData.upsert({
            where: { userId },
            update: {
                username: user.login,
                avatarUrl: user.avatar_url,
                bio: user.bio,
                publicRepos: user.public_repos,
                followers: user.followers,
                following: user.following,
                repos: JSON.parse(JSON.stringify(repos)),
                languages: JSON.parse(JSON.stringify(languages)),
                contributions: JSON.parse(JSON.stringify(contributions)),
                lastSyncAt: new Date(),
            },
            create: {
                userId,
                username: user.login,
                avatarUrl: user.avatar_url,
                bio: user.bio,
                publicRepos: user.public_repos,
                followers: user.followers,
                following: user.following,
                repos: JSON.parse(JSON.stringify(repos)),
                languages: JSON.parse(JSON.stringify(languages)),
                contributions: JSON.parse(JSON.stringify(contributions)),
            },
        });
    }
}

/**
 * Get access token for a user from their GitHub account
 */
export async function getGitHubAccessToken(userId: string): Promise<string | null> {
    const account = await prisma.account.findFirst({
        where: {
            userId,
            provider: "github",
        },
    });

    return account?.access_token || null;
}

/**
 * Sync GitHub data for a user
 */
export async function syncGitHubData(userId: string): Promise<boolean> {
    const accessToken = await getGitHubAccessToken(userId);

    if (!accessToken) {
        throw new Error("No GitHub account linked");
    }

    const github = new GitHubService(accessToken);
    await github.syncAllData(userId);

    return true;
}

/**
 * Get cached GitHub data for a user
 */
export async function getGitHubData(userId: string) {
    return prisma.githubData.findUnique({
        where: { userId },
    });
}
