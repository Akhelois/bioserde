const { spawn } = require("child_process");
const path = require("path");

console.log("Starting Flask backend...");
const backendProcess = spawn("python", ["app.py"], {
  stdio: "inherit",
  shell: true,
});

backendProcess.on("error", (err) => {
  console.error("Failed to start backend:", err);
});

console.log("Starting Next.js frontend...");
const frontendProcess = spawn("npm", ["run", "dev"], {
  stdio: "inherit",
  shell: true,
});

frontendProcess.on("error", (err) => {
  console.error("Failed to start frontend:", err);
});

const cleanup = () => {
  console.log("Shutting down services...");
  backendProcess.kill();
  frontendProcess.kill();
};

process.on("SIGINT", cleanup);
process.on("SIGTERM", cleanup);
