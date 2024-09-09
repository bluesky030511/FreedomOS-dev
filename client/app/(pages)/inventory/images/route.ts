import { NextResponse, type NextRequest } from 'next/server';

import { getBlobClient } from '@/app/(util)/azure';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const container = searchParams.get('container');
  const blob = searchParams.get('blob');

  if (!container || !blob) return NextResponse.json({ error: 'Missing container or blob' }, { status: 400 });

  const blobClient = getBlobClient({
    containerName: container,
    blobName: blob,
  });

  const buffer = await blobClient.downloadToBuffer();

  const response = new NextResponse(buffer);

  return response;
}
