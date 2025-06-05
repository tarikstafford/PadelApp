export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-background border-t">
      <div className="container mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <p className="text-center text-sm text-muted-foreground">
          &copy; {currentYear} PadelGo. All rights reserved.
        </p>
        {/* Additional footer links or info can go here */}
      </div>
    </footer>
  );
} 