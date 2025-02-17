import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        try {
          const res = await fetch("http://localhost:8000/api/v2/auth/login/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials?.email,
              password: credentials?.password,
            }),
          })

          const data = await res.json()

          if (res.ok && data.status === 'success') {
            return {
              id: data.user.email,
              email: data.user.email,
              first_name: data.user.first_name,
              last_name: data.user.last_name,
              is_staff: data.user.is_staff,
              is_superuser: data.user.is_superuser,
              groups: data.user.groups,
              accessToken: data.token,
              refreshToken: data.refresh,
            }
          }
          throw new Error(data.message || "Authentication failed")
        } catch (error) {
          throw new Error(error as string)
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken;
        token.refreshToken = user.refreshToken;
        token.first_name = user.first_name;
        token.last_name = user.last_name;
        token.is_staff = user.is_staff;
        token.is_superuser = user.is_superuser;
        token.groups = user.groups;
      }
      return token;
    },
    async session({ session, token }) {
      if (session) {
        session.accessToken = token.accessToken as string;
        session.refreshToken = token.refreshToken as string;
        session.user.first_name = token.first_name as string;
        session.user.last_name = token.last_name as string;
        session.user.is_staff = token.is_staff as boolean;
        session.user.is_superuser = token.is_superuser as boolean;
        session.user.groups = token.groups as string[];
      }
      return session;
    }
  },
  pages: {
    signIn: "/",
  },
})

export { handler as GET, handler as POST }

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    refreshToken?: string;
    user: {
      email?: string | null;
      first_name?: string;
      last_name?: string;
      is_staff?: boolean;
      is_superuser?: boolean;
      groups?: string[];
    }
  }

  interface User {
    accessToken?: string;
    refreshToken?: string;
    first_name?: string;
    last_name?: string;
    is_staff?: boolean;
    is_superuser?: boolean;
    groups?: string[];
  }
}
