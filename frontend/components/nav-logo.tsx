import Link from "next/link";
import { FlaskConical } from "lucide-react";

export default function NavLogo() {
  return (
    <div className="flex items-center p-2">
      <Link href="/samples/dashboard" className="flex items-center space-x-2">
        <FlaskConical className="h-4 w-4" />
        <span className="text-lg font-semibold">G-Trac</span>
      </Link>
    </div>
  );
}
