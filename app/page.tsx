import { DashboardHeader } from "@/components/dashboard-header";
import { DashboardSidebar } from "@/components/dashboard-sidebar";
import { OverviewCards } from "@/components/overview-cards";
import { ProductionChart } from "@/components/production-chart";
import { SystemStatus } from "@/components/system-status";
import { EnvironmentalImpact } from "@/components/environmental-impact";
import { AIInsights } from "@/components/ai-insights";
import { RecentAlerts } from "@/components/recent-alerts";
import { SidebarProvider } from "@/components/ui/sidebar";

export default function Dashboard() {
  return (
    <SidebarProvider defaultOpen={true}>
      <div className="min-h-screen bg-gray-50 flex">
        <DashboardSidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <DashboardHeader />
          <main className="flex-1 overflow-y-auto p-4 lg:p-6">
            <div className="max-w-7xl mx-auto space-y-6">
              <div className="mb-6">
                <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">
                  Dashboard Overview
                </h1>
                <p className="text-gray-600 mt-2">
                  Monitor your Bioserde system performance and energy production
                </p>
              </div>

              <OverviewCards />

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <ProductionChart />
                </div>
                <div>
                  <SystemStatus />
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <EnvironmentalImpact />
                <AIInsights />
              </div>

              <RecentAlerts />
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
