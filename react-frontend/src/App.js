import Title from './components/title';
import Body from './components/body';

import './index.css';
import { useState } from 'react';

function App() {
  return (
    <div className="flex flex-col items-center">
      <Title />
      <Body />
    </div>
  );
}

export default App;
