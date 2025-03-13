import PageNotFound404 from "@/ui/components/PageNotFound404";
import SideNavBar from "@/ui/components/SideNavBar";
import { Outlet, createRootRoute } from "@tanstack/react-router";

export const Route = createRootRoute({
  component: RootComponent,
  notFoundComponent: PageNotFound404,
});

function RootComponent() {
  return (
    <main className="h-screen w-screen p-4 flex flex-row gap-4 grow box-border">
      <SideNavBar />
      <section className=" w-full text-neutral-100 flex overflow-auto">
        <Outlet />
      </section>
    </main>
  );
}

// bg-zinc-800 rounded-xl
// overflow-auto
