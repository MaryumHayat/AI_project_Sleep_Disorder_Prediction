const form = document.getElementById("predictionForm");
if (form) {
    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        
        const emoji = document.getElementById("emoji");
        const text = document.getElementById("statusText");
        const diagResult = document.getElementById("diagnosisResult");
        const loader = document.getElementById("loadingDots");

        // Show dots, reset text
        loader.style.display = "flex";
        text.innerText = "Processing...";
        diagResult.innerText = "...";

        const formData = new FormData(form);
        try {
            const response = await fetch('/predict', { method: 'POST', body: formData });
            const data = await response.json();
            
            setTimeout(() => {
                loader.style.display = "none";
                text.innerText = data.diagnosis;
                diagResult.innerText = data.diagnosis;

                emoji.innerText = data.diagnosis === "No Disorder" ? "😌" : 
                                 data.diagnosis === "Obstructive Sleep Apnea" ? "😤" : "😵‍💫";
            }, 2000);

        } catch (error) {
            loader.style.display = "none";
            text.innerText = "Connection Error";
        }
    });
}

function scrollToForm() {
    document.getElementById("formSection").scrollIntoView({ behavior: "smooth" });
}

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = "1";
            entry.target.style.transform = "translateY(0)";
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.form-section, .result-section').forEach(section => {
    section.style.opacity = "0";
    section.style.transform = "translateY(30px)";
    section.style.transition = "all 0.8s ease-out";
    observer.observe(section);
});