/* eslint-disable no-console */
/* eslint quotes: ["error", "single"] */
/* global window, document */
/* globals process: readonly */
/* exported setup */
// @ts-check
// @ts-nocheck
/* eslint-env node */
/* @jsx h */
/** @jsxImportSource preact */
// global state is shared between the tests. This line is prose.
const values = [];
// eslint-disable-next-line no-unused-vars
const unused = 1;
const used = 2; // eslint-disable-line no-unused-vars
// @ts-ignore
values.push(used);
// @ts-expect-error: values holds numbers
values.push('a');
// prettier-ignore
const matrix = [1,0,
                0,1];
/* istanbul ignore next */
function ignored() {}
/* c8 ignore start */
function alsoIgnored() {}
/* c8 ignore stop */
const pure = /*#__PURE__*/ Object.freeze({});
const purer = /* @__PURE__ */ Object.freeze({});
const chart = import(/* webpackChunkName: "chart" */ './chart.js');
const later = import(/* @vite-ignore */ './later.js');
/* eslint-enable no-console */
// #region helpers
function helper() {
  return [values, unused, matrix, ignored, alsoIgnored, pure, purer, chart, later];
}
// #endregion
//# sourceMappingURL=pragmas.js.map
