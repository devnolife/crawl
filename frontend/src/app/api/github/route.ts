import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { syncGitHubData, getGitHubData } from "@/lib/github";

export const dynamic = "force-dynamic";

/**
 * GET /api/github - Get cached GitHub data for authenticated user
 */
export async function GET() {
    const session = await auth();

    if (!session?.user?.id) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const data = await getGitHubData(session.user.id);

    if (!data) {
        return NextResponse.json({ error: "No GitHub data found" }, { status: 404 });
    }

    return NextResponse.json(data);
}

/**
 * POST /api/github/sync - Sync GitHub data for authenticated user
 */
export async function POST() {
    const session = await auth();

    if (!session?.user?.id) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    try {
        await syncGitHubData(session.user.id);
        const data = await getGitHubData(session.user.id);
        return NextResponse.json({ success: true, data });
    } catch (error) {
        const message = error instanceof Error ? error.message : "Sync failed";
        return NextResponse.json({ error: message }, { status: 500 });
    }
}
