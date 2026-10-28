import { server } from "./build/index.js";

// Node ends requests after 5 minutes by default, which cuts off large uploads on slow connections
server.requestTimeout = 60 * 60 * 1000;
