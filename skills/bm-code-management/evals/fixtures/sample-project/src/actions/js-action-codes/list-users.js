import { executeAction } from "@basemachina/action";

/** @type { import("@basemachina/action").Handler } */
export default async (args, { vars, secrets }) => {
  if (args.email && !args.email.includes("@")) {
    return { userError: "email looks invalid" };
  }
  const results = await executeAction("fetch-users", { email: args.email });
  if (!results[0].success) {
    return { resultError: "fetch-users returned no data" };
  }
  return results[0].success;
};
