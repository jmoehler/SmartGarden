async function getAllTemplates() {
    try {
        const response = await fetch('/get_all_templates');
        const data = await response.json();
        return data.templates;
    } catch (error) {
        console.log("Error fetching all templates: ", error);
        throw error; // Rethrow the error for handling at a higher level
    }
}


function createCarouselCard(min, max, sensortype, active) {
    const card = document.createElement('div');
    card.classList.add("card", "me-2");
    if (active == 0) card.classList.add("bg-secondary")
    
    const cardBody = document.createElement('div');
    cardBody.classList.add("card-body", "text-dark", "p-2", "px-4");
    
    const cardTitle = document.createElement('h5');
    cardTitle.classList.add("card-title");
    cardTitle.innerHTML = `${sensortype}`;
    
    const cardText = document.createElement('p');
    cardText.classList.add("card-text");
    cardText.innerHTML = `${min} - ${max}`;
    
    cardBody.append(cardTitle, cardText);
    card.appendChild(cardBody);

    return card;
}

async function displayTemplatesInCarousel(){
    let templates = await getAllTemplates();
    console.log(templates)
    const carouselIndicators = document.getElementById('carousel-indicators');
    const carouselInner = document.getElementById('carousel-inner');
    templates.forEach((template, index) => {
        // creation of indicator button
        const indicator = Object.assign({}, {
            type: "button",
            "data-bs-target": "#carouselExampleIndicators",
            "data-bs-slide-to": `${index}`,
            class: template.active ? "active" : "",
            "aria-current": template.active ? "true" : "false",
            "aria-label": `Slide ${index + 1}`
        });

        const buttonElement = document.createElement("button");

        Object.keys(indicator).forEach(attribute => {
            buttonElement.setAttribute(attribute, indicator[attribute]);
        });

        carouselIndicators.appendChild(buttonElement);
        
        // creation of carousel item
        let carouselItem = document.createElement('div');
        if (template.active == 1){
            carouselItem.classList.add("carousel-item", "active");
            carouselItem.id = `${template.template_name}`
        }
        else{
            carouselItem.classList.add("carousel-item");
            carouselItem.id = `${template.template_name}`
        }
        
        
        // creation of cards
        const card1 = createCarouselCard(template.ph_min, template.ph_max, "pH", template.active)
        const card2 = createCarouselCard(template.ec_min, template.ec_max, "EC", template.active)
        const card3 = createCarouselCard(template.hum_min, template.hum_max, "Humidity", template.active)
        const card4 = createCarouselCard(template.temp_min, template.temp_max, "Temperature", template.active)
        const card5 = createCarouselCard(template.light_on, template.light_off, "Light", template.active)
        
        
        
        const styleDiv = document.createElement('div')
        styleDiv.classList.add("d-flex", "justify-content-evenly", "flex-nowrap", "mt-3")
        
        
        const template_name = document.createElement('h4')
        if (template.active == 1){
            template_name.innerHTML = `${template.template_name} (Active)`;
            template_name.classList.add("mx-2")
        } else {
            template_name.innerHTML = `${template.template_name}`;
            template_name.classList.add("mx-2", "text-secondary")
        }


        styleDiv.append(card1, card2, card3, card4, card5);
        carouselItem.append(template_name, styleDiv);
        carouselInner.appendChild(carouselItem);
    });
}

function createCheckbox(template_name, active){
    const checkboxDiv = document.createElement('div');
    checkboxDiv.classList.add("form-check");

    const checkbox = document.createElement('input');
    checkbox.classList.add('form-check-input');
    checkbox.type = 'checkbox';
    checkbox.value = `${template_name}`; 
    checkbox.name = 'inputs';
    
    const label = document.createElement('label');
    label.classList.add('form-check-label');
    label.innerHTML = `${template_name}`
    if (active){
        label.innerHTML = `${template_name} (currently active)`
        checkbox.disabled = true;
    }

    checkboxDiv.append(checkbox, label);
    return checkboxDiv;

}

// creates checkboxes template_deletion modal
async function loadModalCheckboxes(){
    let templates = await getAllTemplates();
    const templateDeletionForm = document.getElementById('template-delete-form');
    templates.forEach(template => {
        let checkbox;
        if (template.active === 1)
            checkbox = createCheckbox(template.template_name, true);
        else
            checkbox = createCheckbox(template.template_name, false);

        templateDeletionForm.appendChild(checkbox);
    })
}

function createToggle(template_name, active){
    const toggleDiv = document.createElement('div');
    toggleDiv.classList.add("form-check");

    const toggle = document.createElement('input');
    toggle.classList.add('form-check-input');
    toggle.type = 'radio';
    toggle.value = `${template_name}`; 
    toggle.name = 'inputs';
    
    const label = document.createElement('label');
    label.classList.add('form-check-label');
    label.innerHTML = `${template_name}`
    if (active){
        label.innerHTML = `${template_name} (currently active)`
        toggle.checked = true;
        toggle.disabled = true;
    }

    toggleDiv.append(toggle, label);
    return toggleDiv;

}

// creates radio toggles on template_activation modal
async function loadModalToggles(){
    let templates = await getAllTemplates();
    const templateActivationForm = document.getElementById('template-activation-form');
    templates.forEach(template => {
        let toggle;
        if (template.active === 1)
            toggle = createToggle(template.template_name, true);
        else
            toggle = createToggle(template.template_name, false);

        templateActivationForm.appendChild(toggle);
    })
}


displayTemplatesInCarousel();