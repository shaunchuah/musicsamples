"use client";

import { Sample, columns } from "./columns";
import { DataTable } from "@/components/ui/data-table";
import { getSession, signIn, signOut } from "next-auth/react"; // Add this import at the top
import { useState, useEffect } from "react";

interface ApiResponse {
  data: Sample[];
}

async function getData(): Promise<ApiResponse> {
  const session = await getSession();
  if (!session) {
    // Redirect to sign in if no session
    signIn();
    throw new Error("No session found");
  }

  try {
    const options = {
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
    };
    const response = await fetch(
      "http://localhost:8000/api/v2/samples/",
      options
    );

    if (response.status === 401) {
      // Token is invalid or expired
      signOut(); // Clear session
      await signIn(); // Force reauthentication
      throw new Error("Session expired");
    }

    if (!response.ok) {
      throw new Error("Failed to fetch data");
    }

    const data: ApiResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
}

export default function Page() {
  const [data, setData] = useState<ApiResponse | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const result = await getData();
      setData(result);
    };
    fetchData();
  }, []);

  return (
    <>
      <h1>Dashboard</h1>
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="aspect-video rounded-xl bg-muted/50" />
        <div className="aspect-video rounded-xl bg-muted/50" />
        <div className="aspect-video rounded-xl bg-muted/50" />
      </div>
      <div className="min-h-[100vh] flex-1 rounded-xl bg-white md:min-h-min">
        <DataTable columns={columns} data={data || []} />
      </div>
    </>
  );
}
