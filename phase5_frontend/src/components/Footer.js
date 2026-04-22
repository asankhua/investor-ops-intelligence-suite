import React from 'react';
import styled from 'styled-components';
import { FileText } from 'lucide-react';
import { Link } from 'react-router-dom';

const FooterContainer = styled.footer`
  position: fixed;
  bottom: 0;
  left: 60px;
  right: 0;
  height: 40px;
  background: #FFFFFF;
  border-top: 1px solid #E5E5E5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
`;

const FooterLeft = styled.div`
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #6B7280;
`;

const FooterCenter = styled.div`
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #1E3A5F;
  font-weight: 500;
`;

const FooterRight = styled.div`
  display: flex;
  align-items: center;
`;

const LicenseLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #1E3A5F;
  text-decoration: none;
  transition: color 0.2s ease;

  &:hover {
    color: #2980B9;
    text-decoration: underline;
  }
`;

const Footer = () => {
  return (
    <FooterContainer>
      <FooterLeft>
        © 2026 All rights reserved
      </FooterLeft>
      <FooterCenter>
        Ashish Kumar Sankhua
      </FooterCenter>
      <FooterRight>
        <LicenseLink to="/license">
          <FileText size={14} />
          LICENSE
        </LicenseLink>
      </FooterRight>
    </FooterContainer>
  );
};

export default Footer;
