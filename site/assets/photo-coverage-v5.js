/* Local filter only: never fetch photos, write PSN, upload or post on X. */
(() => {
  "use strict";
  const root=document.querySelector("[data-photo-coverage]");
  if (!root) return;
  const filter=root.querySelector("[data-pc-filter]");
  const groups=[...root.querySelectorAll("[data-pc-guide]")];
  const tasks=[...root.querySelectorAll("[data-pc-task]")];
  const text=root.querySelector("[data-pc-shown]");
  function draw() {
    const wanted=filter.value;
    let total=0;
    for (const task of tasks) {
      const show=wanted==="all"||task.dataset.pcPriority===wanted;
      task.hidden=!show;
      if (show) total+=1;
    }
    for (const group of groups) group.hidden=![...group.querySelectorAll("[data-pc-task]")].some(x=>!x.hidden);
    text.textContent=total+" richieste visibili su "+tasks.length;
  }
  filter.addEventListener("change",draw);
  draw();
})();
