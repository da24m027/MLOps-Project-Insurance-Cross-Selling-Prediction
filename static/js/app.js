// static/js/app.js

function app() {
    return {
        form: {
            name: '',
            mobile: '',
            age: 30,
            gender: 'Male',
            driving_license: 1,
            region_code: 28,
            previously_insured: 0,
            vehicle_age: "< 1 Year",
            vehicle_damage: "Yes",
            annual_premium: 30000,
            policy_sales_channel: 152,
            vintage: 100
        },
        showResult: false,
        resultCustomer: '',
        prediction: false,
        positiveCustomers: [],
        allCustomers: [],
        showAllEntries: false,
        
        init() {
            this.fetchPositiveCustomers();
            this.fetchAllCustomers();
        },
        
        async submitForm() {
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: this.form.name,
                        mobile: this.form.mobile,
                        age: parseInt(this.form.age),
                        gender: this.form.gender,
                        driving_license: parseInt(this.form.driving_license),
                        region_code: parseFloat(this.form.region_code),
                        previously_insured: parseInt(this.form.previously_insured),
                        vehicle_age: this.form.vehicle_age,
                        vehicle_damage: this.form.vehicle_damage,
                        annual_premium: parseFloat(this.form.annual_premium),
                        policy_sales_channel: parseFloat(this.form.policy_sales_channel),
                        vintage: parseInt(this.form.vintage)
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.resultCustomer = this.form.name;
                    this.prediction = data.prediction;
                    this.showResult = true;
                    
                    // Refresh data
                    this.fetchPositiveCustomers();
                    this.fetchAllCustomers();
                    
                    // Reset form
                    this.resetForm();
                }
            } catch (error) {
                console.error('Error submitting form:', error);
                alert('An error occurred while processing your request');
            }
        },
        
        async fetchPositiveCustomers() {
            try {
                const response = await fetch('/positive-customers');
                this.positiveCustomers = await response.json();
            } catch (error) {
                console.error('Error fetching positive customers:', error);
            }
        },
        
        async fetchAllCustomers() {
            try {
                const response = await fetch('/customers');
                this.allCustomers = await response.json();
            } catch (error) {
                console.error('Error fetching all customers:', error);
            }
        },
        
        resetForm() {
            // Only reset customer information but keep model parameters
            this.form.name = '';
            this.form.mobile = '';
        }
    };
}