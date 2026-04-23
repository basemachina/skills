import { defineConfig } from "@basemachina/sdk/oac";
import { listUsersAction } from "./src/actions/list-users";

// NOTE: this project.id is a DUMMY used only for eval fixtures.
// Replace with your real project id when copying this structure to a real bm project.
export default defineConfig({
  project: { id: "c0000000000000000000" },
  actions: [listUsersAction],
});
