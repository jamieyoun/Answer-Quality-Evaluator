import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

export async function GET() {
  try {
    const root = path.resolve(process.cwd(), "..");
    const filePath = path.join(root, "data", "evalset", "questions.jsonl");
    const raw = await fs.readFile(filePath, "utf-8");
    const questions = raw
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line));

    return NextResponse.json({ questions });
  } catch (err) {
    console.error("Failed to load questions.jsonl", err);
    return NextResponse.json(
      { error: "Failed to load questions" },
      { status: 500 }
    );
  }
}

