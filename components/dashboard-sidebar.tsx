"use client"

import {
  BarChart3,
  Leaf,
  Monitor,
  Zap,
  TrendingUp,
  Settings,
  AlertTriangle,
  Database,
  Calendar,
  HelpCircle,
} from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const menuItems = [
  {
    title: "Overview",
    icon: BarChart3,
    href: "#",
    isActive: true,
  },
  {
    title: "Production",
    icon: Zap,
    href: "#",
  },
  {
    title: "System Monitor",
    icon: Monitor,
    href: "#",
  },
  {
    title: "Analytics",
    icon: TrendingUp,
    href: "#",
  },
  {
    title: "Environmental",
    icon: Leaf,
    href: "#",
  },
  {
    title: "Alerts",
    icon: AlertTriangle,
    href: "#",
  },
]

const dataItems = [
  {
    title: "Historical Data",
    icon: Database,
    href: "#",
  },
  {
    title: "Reports",
    icon: Calendar,
    href: "#",
  },
]

export function DashboardSidebar() {
  return (
    <Sidebar className="border-r border-gray-200">
      <SidebarHeader className="border-b border-gray-200 pb-4">
        <div className="flex items-center space-x-2">
          <div className="bg-green-600 p-2 rounded-lg">
            <Leaf className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Bioserde</h2>
            <p className="text-sm text-gray-600">Control Panel</p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Dashboard</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={item.isActive}>
                    <a href={item.href} className="flex items-center space-x-3">
                      <item.icon className="h-5 w-5" />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Data & Reports</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {dataItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.href} className="flex items-center space-x-3">
                      <item.icon className="h-5 w-5" />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-gray-200">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <a href="#" className="flex items-center space-x-3">
                <Settings className="h-5 w-5" />
                <span>Settings</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <a href="#" className="flex items-center space-x-3">
                <HelpCircle className="h-5 w-5" />
                <span>Help & Support</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
