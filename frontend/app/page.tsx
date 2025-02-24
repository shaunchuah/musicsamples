"use client";

import { GalleryVerticalEnd } from "lucide-react"
import { LoginForm } from "@/components/login-form"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function LoginPage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    const checkAuthAndRedirect = async () => {
      if (status === "authenticated" && session?.accessToken) {
        try {
          const response = await fetch('/api/auth/verify/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              token: session.accessToken
            })
          });

          if (response.ok) {
            router.push("/samples/dashboard")
          }
        } catch (error) {
          console.error('Error verifying token:', error);
        }
      }
    }

    checkAuthAndRedirect();
  }, [status, session, router])

  // Show loading state while checking session
  if (status === "loading") {
    return <div>Loading...</div>
  }

  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6 md:p-10">
      <div className="flex w-full max-w-sm flex-col gap-6">
        <a href="#" className="flex items-center gap-2 self-center font-medium">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <GalleryVerticalEnd className="size-4" />
          </div>
          G-Trac
        </a>
        <LoginForm />
      </div>
    </div>
  )
}
