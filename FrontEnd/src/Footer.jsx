import React from "react";
import "./Footer.css";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-info">
          <h3>Rock Symphony</h3>
          <p>&copy; {currentYear} Rock Symphony. Todos os direitos reservados.</p>
        </div>
        <div className="footer-contact">
          <p>Suporte:</p>
          <a href="mailto:leonahoum@gmail.com" className="support-email">
            leonahoum@gmail.com
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
