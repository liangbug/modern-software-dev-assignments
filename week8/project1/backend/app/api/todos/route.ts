import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function OPTIONS() {
  return NextResponse.json({}, { headers: CORS_HEADERS });
}

export async function GET() {
  const todos = await prisma.todo.findMany({ orderBy: { createdAt: 'desc' } });
  return NextResponse.json(todos, { headers: CORS_HEADERS });
}

export async function POST(request: Request) {
  try {
    const { title } = await request.json();
    if (!title) return NextResponse.json({ error: 'Title is required' }, { status: 400 });

    const todo = await prisma.todo.create({ data: { title } });
    return NextResponse.json(todo, { status: 201, headers: CORS_HEADERS });
  } catch (e) {
    return NextResponse.json({ error: 'Failed to create todo' }, { status: 500 });
  }
}
