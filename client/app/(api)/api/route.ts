export const dynamic = "force-dynamic"; // defaults to auto
import { cookies } from "next/headers";

export async function GET(request: Request) {
  const cookieStore = cookies();

  return Response.json({ message: "Hello, World!" });
}
