import test from "node:test";
import assert from "node:assert/strict";
import { apiErrorMessage } from "./errors.js";

test("preserves a readable scheduling error returned by the server", () => {
    assert.equal(apiErrorMessage({ response: { status: 503, data: { detail: "Database update required." } } }), "Database update required.");
});

test("explains a network failure without assuming a post failed to save", () => {
    const result = apiErrorMessage({ code: "ERR_NETWORK", message: "Network Error" });
    assert.match(result, /backend/);
    assert.match(result, /Posting records/);
    assert.doesNotMatch(result, /was not scheduled/);
});

test("formats validation errors as text instead of rendering objects", () => {
    assert.equal(apiErrorMessage({ response: { data: { detail: [{ msg: "Invalid time" }, { msg: "Select media" }] } } }), "Invalid time. Select media");
    assert.equal(apiErrorMessage({ response: { data: { detail: { message: "Reconnect" } } } }), "Reconnect");
});

test("keeps local errors readable and handles missing errors", () => {
    assert.equal(apiErrorMessage(new Error("Choose a future time")), "Choose a future time");
    assert.equal(apiErrorMessage(null, "Unable to schedule"), "Unable to schedule");
});
