import React from 'react';
import styled from 'styled-components';
import { FileText, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px 80px 20px;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 600;
  color: #1E3A5F;
  margin: 0;
`;

const BackLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #1E3A5F;
  text-decoration: none;
  margin-bottom: 20px;
  transition: color 0.2s ease;

  &:hover {
    color: #2980B9;
  }
`;

const LicenseCard = styled.div`
  background: #FFFFFF;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #E5E5E5;
`;

const LicenseTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: #1E3A5F;
  margin: 0 0 20px 0;
  text-align: center;
`;

const LicenseText = styled.pre`
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  padding: 0;
`;

const Copyright = styled.p`
  font-size: 14px;
  color: #6B7280;
  text-align: center;
  margin: 30px 0 0 0;
  padding-top: 20px;
  border-top: 1px solid #E5E5E5;
`;

const License = () => {
  const licenseText = `MIT License

Copyright (c) 2026 Ashish Kumar Sankhua

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.`;

  return (
    <Container>
      <BackLink to="/">
        <ArrowLeft size={16} />
        Back to Dashboard
      </BackLink>

      <Header>
        <FileText size={32} color="#1E3A5F" />
        <Title>License</Title>
      </Header>

      <LicenseCard>
        <LicenseTitle>MIT License</LicenseTitle>
        <LicenseText>{licenseText}</LicenseText>
        <Copyright>© 2026 Ashish Kumar Sankhua. All rights reserved.</Copyright>
      </LicenseCard>
    </Container>
  );
};

export default License;
