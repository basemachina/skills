import { defineAction, readFile } from "@basemachina/sdk/oac";

export const listUsersAction = defineAction({
  id: "list-users",
  name: "List users",
  class: "javascript",
  code: readFile("./js-action-codes/list-users.js"),
  parameters: [
    { type: "TEXT", name: "email", required: false },
  ],
});
