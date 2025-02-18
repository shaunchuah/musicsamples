import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { usePathname } from "next/navigation";
import { Fragment } from "react";

function capitalizeSpecialCases(word: string): string {
  // Add special cases here
  const specialCases: Record<string, string> = {
    qr: "QR",
    // Add more special cases as needed
    // 'api': 'API',
    // 'url': 'URL',
  };

  return (
    specialCases[word.toLowerCase()] ||
    word.charAt(0).toUpperCase() + word.slice(1)
  );
}

function generateBreadcrumbs(pathname: string) {
  // Remove trailing slash and split path into segments
  const paths = pathname.replace(/\/$/, "").split("/").filter(Boolean);

  return paths.map((path, index) => {
    // Create the full path up to this point
    const href = `/${paths.slice(0, index + 1).join("/")}`;

    // Format the title: replace underscores and hyphens with spaces, then capitalize each word
    const title = path
      .replace(/[-_]/g, " ") // Replace both hyphens and underscores with spaces
      .split(" ")
      .map(capitalizeSpecialCases)
      .join(" ");

    return { href, title };
  });
}

export default function AuthenticatedLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const breadcrumbs = generateBreadcrumbs(pathname);

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                {breadcrumbs.map((breadcrumb, index) => (
                  <Fragment key={breadcrumb.href}>
                    <BreadcrumbItem className="hidden md:block">
                      {index === breadcrumbs.length - 1 ? (
                        <BreadcrumbPage>{breadcrumb.title}</BreadcrumbPage>
                      ) : (
                        <BreadcrumbLink href={breadcrumb.href}>
                          {breadcrumb.title}
                        </BreadcrumbLink>
                      )}
                    </BreadcrumbItem>
                    {index < breadcrumbs.length - 1 && (
                      <BreadcrumbSeparator className="hidden md:block" />
                    )}
                  </Fragment>
                ))}
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
