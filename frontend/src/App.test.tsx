import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { AuthProvider } from "./lib/auth";
import { LandingPage } from "./pages/LandingPage";

describe("LandingPage", () => {
  it("renders platform name", () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <LandingPage />
        </AuthProvider>
      </BrowserRouter>
    );
    expect(screen.getByText("Hack2Hire AI Interview Platform")).toBeInTheDocument();
  });
});
