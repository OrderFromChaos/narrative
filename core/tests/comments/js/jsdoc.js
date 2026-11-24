/**
 * @file Read and write the plan files of a factory.
 */

/**
 * A plan of one factory: the machines and the recipes they run.
 *
 * The plan is read from {@link readPlan} and written by {@link writePlan|the writer}.
 * See [the format]{@link PlanFormat} and {@linkcode Plan.machines}, or
 * {@link https://example.com/plans the published format}.
 *
 * @typedef {Object} Plan
 * @property {string} name - The name of the factory.
 * @property {Array<Machine>} machines The machines, in build order.
 * @property {{x: number, y: number}} [origin] - The corner of the plan on the map.
 */

/**
 * Read a plan file.
 *
 * Unlike <code>JSON.parse</code>, the reader keeps the order of the keys. It returns a
 * Promise<Plan> for the parsed file, with **every** machine in it.
 *
 * - A missing file gives an empty plan.
 * - A malformed file throws.
 *
 * @param {string} path - Where the plan file is.
 * @param {Object} [options={}] - How to read the file.
 * @param {boolean} [options.strict=false] Whether an unknown key is an error.
 * @param {{encoding: string}} format
 * @returns {Promise<Plan>} The plan, with the machines
 *   in file order.
 * @throws {SyntaxError} When the file is not JSON.
 * @deprecated Use {@link openPlan} instead.
 * @since 2.1.0
 * @see writePlan
 * @example
 * // a comment in the sample
 * const plan = await readPlan('plan.json');
 * @example <caption>With options</caption>
 * readPlan('plan.json', { strict: true });
 * @async
 */
async function readPlan(path, options = {}, format = { encoding: 'utf8' }) {
  return { name: path, machines: [], options, format };
}

/**
 * Write a plan file.
 *
 * ```js
 * // a comment in a fenced sample
 * await writePlan(plan, 'plan.json');
 * ```
 *
 * The writer replaces the file.
 * {@inheritDoc readPlan}
 * @param {Plan} plan The plan.
 * @param {string} path
 * @return {Promise<void>}
 * @template T - The type of the plan.
 * @type {(plan: Plan, path: string) => Promise<void>}
 */
async function writePlan(plan, path) {
  return [plan, path];
}

/** @type {number} */
const limit = 10;

/** The number of plans read so far. */
let count = limit;

/**
 * @param {number} count The number of plans.
 */
function setCount(newCount) {
  count = newCount;
}

/*
 * A plain block comment. A @param tag here is prose.
 */
setCount(count);

/** @deprecated */
const legacy = readPlan;
