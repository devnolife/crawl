import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getGitHubData } from "@/lib/github";

const ML_BACKEND_URL = process.env.ML_BACKEND_URL || "http://localhost:8000";

export const dynamic = "force-dynamic";

/**
 * POST /api/analysis - Get ML analysis for user's GitHub data
 */
export async function POST(request: NextRequest) {
    const session = await auth();

    if (!session?.user?.id) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const githubData = await getGitHubData(session.user.id);

    if (!githubData) {
        return NextResponse.json(
            { error: "No GitHub data found. Please sync your GitHub data first." },
            { status: 404 }
        );
    }

    try {
        const { type = "full" } = await request.json();

        // Prepare data for ML backend
        const payload = {
            username: githubData.username,
            repos: githubData.repos,
            languages: githubData.languages,
            contributions: githubData.contributions,
        };

        let endpoint = "/api/full-analysis";
        if (type === "skills") {
            endpoint = "/api/analyze-skills";
        } else if (type === "cv") {
            endpoint = "/api/cv-recommendations";
        }

        // Call ML backend
        const response = await fetch(`${ML_BACKEND_URL}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`ML Backend error: ${response.statusText}`);
        }

        const analysis = await response.json();

        return NextResponse.json(analysis);
    } catch (error) {
        const message = error instanceof Error ? error.message : "Analysis failed";
        return NextResponse.json({ error: message }, { status: 500 });
    }
}
