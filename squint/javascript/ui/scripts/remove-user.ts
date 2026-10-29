// Runs in the ui pod with the dev admin's credentials: `task remove-user EMAIL=...`
// Removing the user through Better Auth runs its delete hooks, which clean up the user's resources.

const [email] = process.argv.slice(2);
if (!email) throw new Error("usage: node scripts/remove-user.ts <email>");

const { ORIGIN, PORT, ADMIN_EMAIL, ADMIN_PASSWORD } = process.env;

async function call(path: string, init: RequestInit = {}) {
  const response = await fetch(`http://localhost:${PORT}/api/auth${path}`, {
    ...init,
    headers: { origin: ORIGIN ?? "", "content-type": "application/json", ...init.headers },
  });
  if (!response.ok) throw new Error(`${path}: ${response.status} ${await response.text()}`);
  return response;
}

const signIn = await call("/sign-in/email", {
  method: "POST",
  body: JSON.stringify({ email: ADMIN_EMAIL, password: ADMIN_PASSWORD }),
});
const cookie = signIn.headers
  .getSetCookie()
  .map((setCookie) => setCookie.split(";")[0])
  .join("; ");

const search = new URLSearchParams({ filterField: "email", filterValue: email });
const found = await call(`/admin/list-users?${search}`, { headers: { cookie } });
const { users } = (await found.json()) as { users: { id: string }[] };
const [user] = users;
if (!user) throw new Error(`no user with email ${email}`);

await call("/admin/remove-user", {
  method: "POST",
  headers: { cookie },
  body: JSON.stringify({ userId: user.id }),
});
console.log(`removed ${email} (${user.id})`);
