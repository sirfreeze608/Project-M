html.page("Auto-Render Test");

html.heading("Smart render() across types", 1);

html.heading("A number", 3);
html.render(42, "Answer");

html.heading("A complex number", 3);
let z = complex(3, 4);
html.render(z, "Impedance Z");

html.heading("A matrix", 3);
let M = matrix([[1, 2], [3, 4]]);
html.render(M, "Rotation Matrix");

html.heading("An array", 3);
html.render([10, 20, 30], "Sensor readings");

html.heading("A hash", 3);
let stats_summary = {"mean": 23.4, "stdev": 1.8, "count": 50};
html.render(stats_summary, "Summary stats");

html.show(["file"]);
print("Render test complete.");
