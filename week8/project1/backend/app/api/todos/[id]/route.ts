import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': 'http://localhost:5173',
  'Access-Control-Allow-Methods': 'GET, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function OPTIONS() {
  return NextResponse.json({}, { headers: CORS_HEADERS });
}

export async function GET(_: Request, { params }: { params: { id: string } }) {
  const todo = await prisma.todo.findUnique({ where: { id: Number(params.id) } });
  if (!todo) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  return NextResponse.json(todo, { headers: CORS_HEADERS });
}

export async function PUT(request: Request, { params }: { params: { id: string } }) {
  try {
    const { title, completed } = await request.json();
    const todo = await prisma.todo.update({
      where: { id: Number(params.id) },
      data: { title, completed }
    });
    return NextResponse.json(todo, { headers: CORS_HEADERS });
  } catch (e) {
    return NextResponse.json({ error: 'Not found or update failed' }, { status: 404 });
  }
}

export async function DELETE(_: Request, { params }: { params: { id: string } }) {
  try {
    await prisma.todo.delete({ where: { id: Number(params.id) } });
    return new NextResponse(null, { status: 204, headers: CORS_HEADERS });
  } catch (e) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
}
