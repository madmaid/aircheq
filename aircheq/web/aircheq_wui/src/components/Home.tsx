import React from "react";
import styled from "styled-components";

import Reserved from "./Reserved";

const HomeContainer = styled.div`
  padding: 0;
`;
const ReservedIndex = styled.div`
  font-size: 20px;
  padding: 0;
  margin: 0;
  color: white;
  background: #60bde5;
`;

const Home = () => (
  <HomeContainer>
    <ReservedIndex>予約済</ReservedIndex>
    <Reserved />
  </HomeContainer>
);

export default Home;
