import React from "react";
import "./OrderStepper.css";

const OrderStepper = ({ pending, sent }) => {
  // Determinar qual step está ativo
  const getActiveStep = () => {
    if (pending) return 0; // Pagamento pendente
    if (!sent) return 1; // Aguardando envio (processado mas não enviado)
    return 2; // Pedido à transportadora (enviado)
  };

  const activeStep = getActiveStep();

  const steps = [
    {
      label: pending ? "Pagamento Pendente" : "Pagamento Identificado",
      description: pending ? "Aguardando confirmação do pagamento" : "Pagamento confirmado e aprovado",
      icon: "💳"
    },
    {
      label: "Aguardando Envio",
      description: "Pedido aprovado, preparando para envio",
      icon: "📦"
    },
    {
      label: "Pedido à Transportadora",
      description: "Produto já enviado e a caminho do seu endereço",
      icon: "🚚"
    }
  ];

  return (
    <div className="order-stepper">
      <div className="stepper-container">
        {steps.map((step, index) => (
          <div key={index} className="step-wrapper">
            <div className={`step ${index <= activeStep ? 'active' : ''} ${index < activeStep ? 'completed' : ''}`}>
              <div className="step-icon">
                {index < activeStep ? '✓' : step.icon}
              </div>
              <div className="step-content">
                <div className="step-label">{step.label}</div>
                <div className="step-description">{step.description}</div>
              </div>
            </div>
            {index < steps.length - 1 && (
              <div className={`step-connector ${index < activeStep ? 'completed' : ''}`}></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderStepper;
